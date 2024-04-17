import unittest
import uuid
import os

from transform.normalizer import FootballMatchesNormalizer


class TestFootballMatchesNormalizer(unittest.TestCase):

    def setUp(self):
        self.fm_normalizer = FootballMatchesNormalizer()

    def test_wrong_file_format(self):
        with self.assertRaises(IOError):
            self.fm_normalizer.filename = "input.txt"

            input_df = self.fm_normalizer.input_df()

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.fm_normalizer.filename = f"{uuid.uuid4()}.csv"

            input_df = self.fm_normalizer.input_df()

    def test_input_df_missing_columns(self):
        with self.assertRaises(ValueError):
            fm_normalizer = FootballMatchesNormalizer(
                filename='test_data/missing_columns.csv')
            
            input_df = fm_normalizer.input_df()

    def test_input_df_null_values(self):
        with self.assertRaises(ValueError):
            fm_normalizer = FootballMatchesNormalizer(
                filename='test_data/null_values.csv')
            
            input_df = fm_normalizer.input_df()

    def test_team_df_columns(self):
        team_columns_list = ["team_id", "team_name"]

        self.assertEqual(team_columns_list, 
            list(self.fm_normalizer.team_df.columns))
        
    def test_match_df_columns(self):
        match_columns_list = ["match_id", "match_name", "home_team_id",
            "away_team_id", "home_goals", "away_goals"]
        
        self.assertEqual(match_columns_list, 
            list(self.fm_normalizer.match_df.columns))
        
    def test_player_df_columns(self):
        player_columns_list = ["player_id", "team_id", "player_name"]

        self.assertEqual(player_columns_list, 
            list(self.fm_normalizer.player_df.columns))
        
    def test_statistic_df_columns(self):
        statistic_columns_list = ["stat_id", "player_id", "match_id", 
            "goals_scored", "minutes_played", "fraction_of_total_minutes",
            "fraction_of_total_goals"]

        self.assertEqual(statistic_columns_list, 
            list(self.fm_normalizer.statistic_df.columns))
        
    def test_match_goals(self):
        """ Check if goals totals on match dataframe are correct """

        input_home_goals = self.fm_normalizer.input_df[
            self.fm_normalizer.input_df.is_home].goals_scored.sum()
        input_away_goals = self.fm_normalizer.input_df[
            ~self.fm_normalizer.input_df.is_home].goals_scored.sum()
        
        match_home_goals = self.fm_normalizer.match_df.home_goals.sum()
        match_away_goals = self.fm_normalizer.match_df.away_goals.sum()

        self.assertEqual(input_home_goals, match_home_goals)
        self.assertEqual(input_away_goals, match_away_goals)

    def test_generate_output_files(self):
        """ Check if output files are generated in the output directory """
        self.fm_normalizer.generate_output_files()

        for output_name in FootballMatchesNormalizer.OUTPUT_DATASET_NAMES_LIST:
            self.assertTrue(os.path.isfile(
                f"{os.getcwd()}/output/{output_name}.jsonl"))


if __name__ == "__main__":
    unittest.main()
