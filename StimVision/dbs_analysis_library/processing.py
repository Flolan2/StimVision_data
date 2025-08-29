# --- REFINED FILE: dbs_analysis_library/processing.py ---

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data loading, parsing, and preprocessing functions for the DBS kinematic analysis.
"""
import os
import glob
import pandas as pd
import re
import sys

def standardize_parameter_names(df):
    """
    Standardizes parameter names from CSV files to a consistent CamelCase format
    using a predefined mapping.
    """
    name_map = {
        'meanamplitude': 'MeanAmplitude', 'stdamplitude': 'StdAmplitude',
        'meanspeed': 'MeanSpeed', 'stdspeed': 'StdSpeed',
        'meanrmsvelocity': 'MeanRMSVelocity', 'stdrmsvelocity': 'StdRMSVelocity',
        'meanopeningspeed': 'MeanOpeningSpeed', 'stdopeningspeed': 'StdOpeningSpeed',
        'meanclosingspeed': 'MeanClosingSpeed', 'stdclosingspeed': 'StdClosingSpeed',
        'meancycleduration': 'MeanCycleDuration', 'stdcycleduration': 'StdCycleDuration',
        'rangecycleduration': 'RangeCycleDuration', 'rate': 'Frequency',
        'amplitudedecay': 'AmplitudeDecay', 'velocitydecay': 'VelocityDecay',
        'ratedecay': 'RateDecay', 'cvamplitude': 'CVAmplitude',
        'cvcycleduration': 'CVCycleDuration', 'cvspeed': 'CVSpeed',
        'cvrmsvelocity': 'CVRMSVelocity', 'cvopeningspeed': 'CVOpeningSpeed',
        'cvclosingspeed': 'CVClosingSpeed'
    }
    df['Attribute'] = df['Attribute'].str.lower().map(name_map).fillna(df['Attribute'])
    return df

def sort_condition_key(condition):
    """
    Provides a sorting key for condition strings to ensure a logical order in plots
    (e.g., DBS Off first, followed by numbered programs).
    """
    condition_lower = str(condition).lower()
    if "dbs off" in condition_lower: return 0
    num_match = re.search(r'(?:pr|level)\s?(\d+)', condition_lower, re.IGNORECASE)
    if num_match: return int(num_match.group(1))
    if "dbs on" in condition_lower: return 100
    if "med on" in condition_lower: return 200
    return 500

def load_csv_files_by_hand(directory):
    """
    Loads all CSV files in a directory, parses filenames to determine experimental
    condition and hand, standardizes parameter names, and organizes the data
    into a nested dictionary.
    """
    file_dict = {}
    if not os.path.isdir(directory):
        print(f"Error: Provided directory does not exist: {directory}")
        return file_dict
        
    csv_files = glob.glob(os.path.join(directory, '*.csv'))
    if not csv_files:
        print(f"Info: No CSV files found in '{os.path.basename(directory)}'.")
        return file_dict
    
    print(f"Found {len(csv_files)} CSVs in '{os.path.basename(directory)}'. Parsing...")

    # Regex patterns for robust filename parsing
    med_off_re = re.compile(r'med[_\s]*off', re.IGNORECASE)
    med_on_re = re.compile(r'med[_\s]*on', re.IGNORECASE)
    dbs_off_re = re.compile(r'dbs[_\s]*off', re.IGNORECASE)
    dbs_on_re = re.compile(r'dbs[_\s]*on', re.IGNORECASE)
    left_re = re.compile(r'left', re.IGNORECASE)
    right_re = re.compile(r'right', re.IGNORECASE)
    extra_cond_re = re.compile(r'(Pr\d+|Level[_\s]?\d+)', re.IGNORECASE)

    conditions_found = set()
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        try:
            df = pd.read_csv(file_path)
            if 'Attribute' not in df.columns or 'Value' not in df.columns: continue
            df = standardize_parameter_names(df)
        except Exception as e:
            print(f"Warning: Could not read or parse '{filename}'. Error: {e}")
            continue

        # Filename parsing logic
        med_cond = "Med On" if med_on_re.search(filename) else "Med Off"
        dbs_cond = "DBS On" if dbs_on_re.search(filename) else "DBS Off"
        extra_match = extra_cond_re.search(filename)
        extra_condition = extra_match.group(1).replace('_', ' ').strip() if extra_match else ""
        
        condition = f"{med_cond} - {dbs_cond}"
        if extra_condition:
             condition += f" - {extra_condition}"
        conditions_found.add(condition)
        
        hand = "Left" if left_re.search(filename) else "Right" if right_re.search(filename) else "Unknown"

        if hand != "Unknown":
            file_dict.setdefault(condition, {}).setdefault(hand, []).append(df)

    print(f"Identified conditions: {', '.join(sorted(list(conditions_found), key=sort_condition_key))}")
    return file_dict