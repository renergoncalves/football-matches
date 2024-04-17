# Football Match Data Normalizer
This application normalizes the football match data found at [input/input.csv](https://github.com/renergoncalves/football-matches/tree/main/input/input.csv) and generates the normalized data as JSON Lines files at the output/ directory.

### Prerequisites

- Python 3.x
- pip

### Installing the python dependencies

1. Navigate to the project directory:

    ```bash
    cd football-matches
    ```

2. Create a virtual environment

    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment

    #### On Linux:   
    ```bash
    source venv/bin/activate
    ```

    #### On Windows:
    ```bash
    venv\Scripts\activate
    ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

```bash
python main.py
```

### Testing the Application

```bash
python -m tests.test_normalizer
```