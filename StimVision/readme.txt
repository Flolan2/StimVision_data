==================================================================
  Video-Based Kinematic Analysis for DBS Programming
==================================================================


The software provides an objective, data-driven workflow to analyze kinematic data from smartphone videos, rank Deep Brain Stimulation (DBS) settings, and generate intuitive visualizations to support clinical decision-making.


## Features

-   **Automated Data Processing:** Loads and parses kinematic data from CSV files, automatically identifying experimental conditions from filenames.
-   **Standardized Kinematics:** Standardizes parameter names to a consistent vocabulary for robust analysis.
-   **Patient-Specific Weighting:** Calculates a "Dynamically Weighted Improvement Score" (DWIS) that prioritizes the kinematic parameters most responsive to stimulation for each individual patient.
-   **Objective Ranking:** Provides a clear, objective ranking of all tested DBS settings based on the DWIS.
-   **Intuitive Visualization:** Generates a publication-quality PDF report for each patient, featuring the "Dynamic Clinical View"—a heatmap that intuitively visualizes the therapeutic effect of the best programs on the most responsive parameters.
-   **Flexible Execution:** Supports both interactive use within an IDE (like Spyder) for clinical workflows and automated command-line execution for batch processing and reproducibility.


## Project Structure

The repository is organized as follows:

project_root/
|
+-- Data/
|   +-- Patient01/
|       |-- Med_Off_DBS_Off_Left.csv
|       |-- Med_Off_DBS_On_Pr1_Left.csv
|       +-- ... (other patient CSV files)
|
+-- Output/
|   +-- Patient01/
|       |-- report_Patient01_engineering_vs_clinical.pdf
|       +-- ... (other output files)
|
+-- dbs_analysis_library/
|   |-- __init__.py
|   |-- analysis.py           # Core DWIS calculation logic
|   |-- processing.py         # Data loading and cleaning
|   |-- visualization.py      # All plotting functions
|   +-- utils.py              # Shared constants and parameter names
|
+-- run_ismr_analyzer.py      # The main executable script
+-- requirements.txt          # Python package dependencies
+-- README.txt                # This file


## Installation

This project requires Python 3.8 or newer.

1.  **Clone the Repository:**
    git clone https://github.com/Flolan2/StimVision_data
    cd your-repository-name

2.  **Create a Virtual Environment (Recommended):**
    # For macOS / Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

3.  **Install Dependencies:**
    A `requirements.txt` file is included to ensure a consistent environment.
    pip install -r requirements.txt


## Usage

The main script `run_ismr_analyzer.py` can be run in two ways.

### 1. Interactive Mode (for IDEs like Spyder)

This mode is designed for clinical or research workflows where you process patients one by one.

1.  Place your patient data folders inside the `Data/` directory (see Input Data Format below).
2.  Open `run_ismr_analyzer.py` in Spyder or your preferred IDE.
3.  Run the script. It will automatically find the `Data` and `Output` folders.
4.  For each patient, the console will display a list of available conditions and prompt you to select the baseline condition. You can also type `skip` to move to the next patient.

### 2. Automated Mode (from the Terminal)

This mode is ideal for batch processing a large number of patients or for ensuring strict reproducibility.

    python run_ismr_analyzer.py /path/to/Data /path/to/Output [OPTIONS]

**Arguments:**

-   `data_folder`: Path to the main data folder containing patient subdirectories.
-   `output_folder`: Path where the analysis results will be saved.

**Options:**

-   `--baseline "Med Off - DBS Off"`: Specifies the baseline condition to use for all patients, overriding the interactive prompt.
-   `--overwrite`: If included, the script will delete and re-create output folders for patients that have already been processed.

**Example:**
    python run_ismr_analyzer.py ./Data ./Output --baseline "Med Off - DBS Off" --overwrite


## Input Data Format

The script expects a specific folder and file structure inside the `Data` directory.

-   **Folder Structure:** Each patient must have their own subfolder within `Data`. The name of the folder will be used as the Patient ID.
    -   `Data/Patient01/`
    -   `Data/Patient02/`

-   **Filename Convention:** The script parses filenames to determine the experimental conditions. Filenames **must** contain keywords indicating:
    -   Medication state: `Med Off` or `Med On`
    -   Stimulation state: `DBS Off` or `DBS On`
    -   Hand: `Left` or `Right`
    -   Program Identifier (optional, for DBS On): `Pr1`, `Pr02`, `Level3`, etc.

    **Valid Filename Examples:**
    -   `Med_Off_DBS_Off_Left_Trial1.csv`
    -   `Med_Off_DBS_On_Pr3_Right.csv`
    -   `Med_On_DBS_On_Level12_Left.csv`


## Output Description

For each patient processed, a subfolder is created in the `Output` directory containing:

-   `report_{PatientID}_engineering_vs_clinical.pdf`: The primary visual report.
    -   (A) Engineering View: A heatmap of improvement vs. baseline, with conditions sorted chronologically. The best-ranked program is highlighted in gold.
    -   (B) Dynamic Clinical View: A re-sorted heatmap that places the most effective programs at the top and the most responsive kinematic parameters on the left, revealing the "kinematic signature" of the best settings.
-   `responsiveness_scores_{hand}.csv`: The standard deviation of improvement for each kinematic parameter, used to calculate the dynamic weights.
-   `optimal_effect_vs_baseline_{hand}.csv`: The raw kinematic change between the best-ranked DBS setting and the baseline.


## License

This project is licensed under the MIT License. See the `LICENSE` file for details.