# --- REFINED FILE (v3): run_ismr_analyzer.py ---
# Implements a hybrid approach:
# - If run from an IDE like Spyder (no arguments), it automatically finds the
#   'Data' and 'Output' folders relative to its location.
# - If run from the command line with paths, it uses those paths.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main executable script for performing individual patient kinematic analysis.

This script is designed for flexible execution:
1. From an IDE (e.g., Spyder): Run the script directly. It will automatically
   locate the 'Data' and 'Output' folders in the parent directory and will
   prompt for baseline selection interactively.
2. From a Terminal: Provide paths to the data and output folders for batch
   processing. The --baseline flag can be used for automated analysis.

Usage (IDE / Spyder):
    Click the 'Run file' button.

Usage (Terminal):
    python run_ismr_analyzer.py /path/to/data /path/to/output --baseline "Med Off - DBS Off"
"""
import os
import sys
import shutil
import argparse

# Ensure the library modules can be found
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path: sys.path.append(script_dir)
except NameError:
    # Fallback for environments where __file__ is not defined
    if '.' not in sys.path: sys.path.append('.')

from dbs_analysis_library.visualization import set_publication_style, create_ismr_patient_report
from dbs_analysis_library.processing import load_csv_files_by_hand
from dbs_analysis_library.analysis import perform_full_hand_analysis

DEFAULT_LAMBDA = 0.1

def get_user_baseline_selection(available_conditions, patient_id):
    """Prompts the user to interactively select a baseline condition for a patient."""
    if not available_conditions:
        return None
        
    print(f"\n--- Please Select a Baseline for Patient: {patient_id} ---")
    for i, cond in enumerate(available_conditions):
        print(f"  {i+1}: {cond}")
        
    default_baseline_name = "Med Off - DBS Off"
    default_idx = available_conditions.index(default_baseline_name) if default_baseline_name in available_conditions else -1

    while True:
        prompt_msg = f"Enter number for baseline"
        if default_idx != -1:
            prompt_msg += f" (default is {default_idx + 1})"
        prompt_msg += ", or 'skip': "
        
        user_input = input(prompt_msg).strip().lower()
        
        if user_input == 'skip':
            return None
        if user_input == "" and default_idx != -1:
            return available_conditions[default_idx]
            
        try:
            selected_num = int(user_input)
            if 1 <= selected_num <= len(available_conditions):
                return available_conditions[selected_num - 1]
            else:
                print("Error: Number is out of range.")
        except ValueError:
            print("Error: Invalid input. Please enter a number or 'skip'.")

def main():
    """Main function to parse arguments and orchestrate the analysis workflow."""
    parser = argparse.ArgumentParser(description="Run video-based kinematic analysis for DBS programming.")
    # --- CHANGE: Make positional arguments optional by using nargs='?' ---
    parser.add_argument("data_folder", nargs='?', default=None, help="Optional: Path to the main data folder.")
    parser.add_argument("output_folder", nargs='?', default=None, help="Optional: Path to the main output folder.")
    parser.add_argument("--baseline", type=str, default='interactive',
                        help="Name of the baseline condition. Default is 'interactive'.")
    parser.add_argument("--overwrite", action="store_true",
                        help="If set, overwrite existing patient output folders.")
    args = parser.parse_args()

    # --- NEW: Logic to handle both command-line args and automatic path finding ---
    if args.data_folder is None or args.output_folder is None:
        print("Info: No command-line paths provided. Using automatic path detection relative to script location.")
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_parent_dir = os.path.dirname(script_dir)
            data_folder = os.path.join(project_parent_dir, "Data")
            output_folder = os.path.join(project_parent_dir, "Output")
            
            if not os.path.isdir(data_folder):
                print(f"Error: Could not find 'Data' folder at expected location: {data_folder}")
                sys.exit(1)
        except NameError:
            print("Fatal: Cannot determine script path in this environment. Please provide data and output folder paths as command-line arguments.")
            sys.exit(1)
    else:
        print("Info: Using command-line paths for data and output.")
        data_folder = args.data_folder
        output_folder = args.output_folder

    set_publication_style()
    os.makedirs(output_folder, exist_ok=True)
    print(f"Data source: {data_folder}")
    print(f"Output destination: {output_folder}\n")

    patient_folders = sorted([f.name for f in os.scandir(data_folder) if f.is_dir()])
    if not patient_folders:
        print(f"Error: No patient subfolders found in '{data_folder}'. Exiting.")
        sys.exit(1)

    for patient_id in patient_folders:
        patient_output_folder = os.path.join(output_folder, patient_id)
        
        if os.path.isdir(patient_output_folder) and not args.overwrite:
            print(f"--- Skipping Patient {patient_id}: Output folder exists. Use --overwrite to re-process. ---")
            continue
        if os.path.isdir(patient_output_folder) and args.overwrite:
            shutil.rmtree(patient_output_folder)

        print(f"\n{'='*15} Processing Patient: {patient_id} {'='*15}")
        os.makedirs(patient_output_folder, exist_ok=True)
        
        patient_data_folder = os.path.join(data_folder, patient_id)
        data_by_condition = load_csv_files_by_hand(patient_data_folder)
        if not data_by_condition:
            print(f"Warning: No valid CSV data found for {patient_id}. Skipping.")
            continue

        available_conditions = sorted(list(data_by_condition.keys()))
        
        if args.baseline == 'interactive':
            baseline_condition = get_user_baseline_selection(available_conditions, patient_id)
            if baseline_condition is None:
                print(f"--- Skipping Patient {patient_id} as requested. ---")
                continue
        else:
            baseline_condition = args.baseline
            if baseline_condition not in available_conditions:
                print(f"Error: Specified baseline '{baseline_condition}' not found for {patient_id}. Skipping.")
                continue
        
        print(f"Using baseline: '{baseline_condition}'")

        # ... (rest of the script is unchanged) ...
        for hand in ["Left", "Right"]:
            results = perform_full_hand_analysis(data_by_condition, hand, baseline_condition, shrinkage_lambda=DEFAULT_LAMBDA)
            
            if not results['responsiveness_scores'].empty:
                results['responsiveness_scores'].to_csv(os.path.join(patient_output_folder, f"responsiveness_scores_{hand.lower()}.csv"))
            
            summary_df = results['summary_df']
            best_on_cond = results['dynamic_ranking_results']['ranked_names'][0] if results['dynamic_ranking_results']['ranked_names'] else None
            
            if best_on_cond and baseline_condition in summary_df.index and best_on_cond in summary_df.index:
                baseline_vals = summary_df.loc[baseline_condition]
                best_on_vals = summary_df.loc[best_on_cond]
                raw_effect = best_on_vals - baseline_vals
                
                raw_effect.to_csv(os.path.join(patient_output_folder, f"optimal_effect_vs_baseline_{hand.lower()}.csv"))
                baseline_vals.to_csv(os.path.join(patient_output_folder, f"baseline_values_{hand.lower()}.csv"))

        create_ismr_patient_report(patient_id, data_by_condition, baseline_condition, patient_output_folder, default_lambda=DEFAULT_LAMBDA)
        
        print(f"--- Finished processing patient {patient_id} ---")
        
    print("\nAnalysis complete.")

if __name__ == '__main__':
    main()