import os

import pandas as pd


class FootballMatchesNormalizer:

    MATCH_TOTAL_MINUTES = 90
    OUTPUT_DATASET_NAMES_LIST = ["match", "team", "player", "statistic"]
    MANDOTORY_INPUT_COLUMNS_SET = {'goals_scored', 'is_home', 'match_id',
        'match_name', 'minutes_played', 'player_id', 'player_name', 'team_id',
        'team_name'}

    def __init__(self, filename="input.csv"):

        self.filename = filename

    @property
    def input_df(self):
        """Reads the input csv file and returns a pandas dataframe."""

        filepath = f"{os.getcwd()}/input/{self.filename}".replace("\\", "/")

        if not self.filename.lower().endswith(".csv"):
            raise IOError("The input file should be of extension '.csv'")
        elif not os.path.isfile(filepath):
            raise FileNotFoundError(
                f"The input csv file could not be found at {filepath}."
            )

        input_df = pd.read_csv(filepath)

        missing_columns_set = (
            FootballMatchesNormalizer.MANDOTORY_INPUT_COLUMNS_SET.difference(
            set(input_df.columns)))

        if missing_columns_set:
            raise ValueError(
                "The following columns are missing in the input data:",
                missing_columns_set
            )
        
        null_values_columns = input_df.isnull().any()

        if null_values_columns.any():
            raise ValueError(
                "The following columns contain null values:",
                list(null_values_columns[null_values_columns == True].index)
            )   

        return input_df

    @property
    def team_df(self):
        """
        Returns a dataframe of the teams with the following columns:

        - team_id -> The Id of the team
        - team_name -> The name of the team
        """

        team_df = (
            self.input_df[["team_id", "team_name"]]
            .drop_duplicates()
            .sort_values(by="team_id", ignore_index=True)
        )

        return team_df

    @property
    def match_df(self):
        """
        Returns a dataframe of the matches with the following columns:

        - match_id -> The unique Id of the match
        - match_name -> The name of the match
        - home_team_id -> The team Id of the home team
        - away_team_id -> The team Id of the away team
        - home_goals -> How many goals the home team scored
        - away_goals -> How many goals the away team scored
        """

        temp_df = self.input_df.copy()

        # It is from common knowledge that the home team is always the first on
        # football match names.
        temp_df["home_team"] = temp_df.match_name.str.split(" vs ").str[0]
        temp_df["away_team"] = temp_df.match_name.str.split(" vs ").str[-1]

        # Merge with team dataframe to get the "team_id" column
        temp_df = temp_df.merge(
            right=self.team_df.rename(
                columns={"team_name": "home_team", "team_id": "home_team_id"}
            )
        )
        temp_df = temp_df.merge(
            right=self.team_df.rename(
                columns={"team_name": "away_team", "team_id": "away_team_id"}
            )
        )

        temp_df.loc[temp_df.is_home, "home_goals"] = temp_df.loc[
            temp_df.is_home, "goals_scored"]
        temp_df.loc[~temp_df.is_home, "away_goals"] = temp_df.loc[
            ~temp_df.is_home, "goals_scored"]

        temp_df.home_goals = temp_df.home_goals.fillna(0).astype(int)
        temp_df.away_goals = temp_df.away_goals.fillna(0).astype(int)

        match_df = temp_df.groupby(
            by=["match_id", "match_name", "home_team_id", "away_team_id"],
            as_index=False,
        )[["home_goals", "away_goals"]].sum()

        return match_df

    @property
    def player_df(self):
        """
        Returns a dataframe of the players with the following columns:

        - player_id -> The Id of the player
        - team_id -> The Id of the team the player plays for
        - player_name -> The name of the player
        """

        player_df = (
            self.input_df[["player_id", "team_id", "player_name"]]
            .drop_duplicates()
            .sort_values(by="player_id", ignore_index=True)
        )

        return player_df

    @property
    def statistic_df(self):
        """
        Returns a dataframe of the statistics with the following columns:

        - stat_id -> A unique Id for each record in the dataset
        - player_id -> The Id of the player the statistic relates to
        - match_id -> The match from which the player statistic originated
        - goals_scored -> How many goals the player scored in the match
        - minutes_played -> How many minutes the player played in the match
        - fraction_of_total_minutes -> What proportion (between 0 and 1) of 
            the 90 minute match the player played 
        - fraction_of_total_goals -> What proportion (between 0 and 1) of
            the total goals scored in the match were scored by the player
        """

        statistic_df = self.input_df[
            ["player_id", "match_id", "goals_scored", "minutes_played"]
        ].reset_index(names=["stat_id"])

        statistic_df.stat_id += 1

        statistic_df["fraction_of_total_minutes"] = (
            statistic_df.minutes_played / FootballMatchesNormalizer.MATCH_TOTAL_MINUTES
        )

        statistic_df = statistic_df.merge(
            right=self.match_df[["match_id", "home_goals", "away_goals"]],
            on=["match_id"],
        )

        statistic_df["total_goals"] = statistic_df.home_goals + statistic_df.away_goals

        statistic_df["fraction_of_total_goals"] = (
            statistic_df.goals_scored / statistic_df.total_goals
        )

        statistic_df.drop(
            columns=["home_goals", "away_goals", "total_goals"], inplace=True
        )

        return statistic_df.sort_values(by='stat_id', ignore_index=True)

    def generate_output_files(self):
        """
        Writes the output files to the output folder in the
        JSON Lines format.
        """

        # Create the output directory if it does not exist
        output_dir = f"{os.getcwd()}/output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for output_name in FootballMatchesNormalizer.OUTPUT_DATASET_NAMES_LIST:
            df = getattr(self, f"{output_name}_df")

            with open(f"{output_dir}/{output_name}.jsonl", "w") as output_file:
                output_file.write(df.to_json(orient="records", lines=True))
