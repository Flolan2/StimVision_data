# --- REFINED FILE: dbs_analysis_library/analysis.py ---

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core analysis functions for calculating improvement, dynamic weights, and
ranking of DBS settings based on kinematic data.
"""
import pandas as pd
import numpy as np
from .processing import sort_condition_key
from .utils import parameter_directions

def aggregate_task_data_by_hand(data_for_task, hand):
    """
    Aggregates kinematic data from multiple CSVs for a specific hand,
    averaging values across trials for each condition.
    """
    aggregated_data = {}
    if not isinstance(data_for_task, dict):
        return pd.DataFrame()

    for condition, hand_dict in data_for_task.items():
        if isinstance(hand_dict, dict) and hand in hand_dict:
            series_list = []
            for df in hand_dict[hand]:
                if isinstance(df, pd.DataFrame) and 'Attribute' in df.columns and 'Value' in df.columns:
                    s = pd.to_numeric(df['Value'], errors='coerce')
                    s.index = df['Attribute']
                    series_list.append(s)
            
            if series_list:
                aggregated_data[condition] = pd.concat(series_list, axis=1).mean(axis=1)

    if not aggregated_data:
        return pd.DataFrame()
    summary_df = pd.DataFrame(aggregated_data).T
    summary_df = summary_df.reindex(sorted(summary_df.index, key=sort_condition_key)).dropna(axis=0, how='all')
    return summary_df

def perform_full_hand_analysis(data_by_condition, hand, baseline, shrinkage_lambda=0.1):
    """
    Performs the complete analysis pipeline for a single hand using a robust,
    integrated workflow with regularized dynamic weighting.

    Args:
        data_by_condition (dict): Nested dict of data: {condition: {hand: [DataFrames]}}.
        hand (str): 'Left' or 'Right'.
        baseline (str): The name of the baseline condition (e.g., "Med Off - DBS Off").
        shrinkage_lambda (float): Regularization parameter (0 to 1). A small value
                                  like 0.1 (default) blends data-driven weights with
                                  uniform weights to prevent over-fitting to noise.

    Returns:
        dict: A dictionary containing all intermediate and final analysis results.
    """
    summary_df = aggregate_task_data_by_hand(data_by_condition, hand)
    
    results = {
        'summary_df': summary_df, 'improvement_df': pd.DataFrame(),
        'responsiveness_scores': pd.Series(dtype=float), 'final_dynamic_weights': pd.Series(dtype=float),
        'dynamic_scores': pd.Series(dtype=float),
        'dynamic_ranking_results': {'ranked_names': [], 'ranked_scores': []}
    }
    
    if summary_df.empty or baseline not in summary_df.index:
        print(f"Warning: No summary data for hand '{hand}' or baseline '{baseline}' not found. Aborting analysis for this hand.")
        return results

    on_conditions = summary_df.index.drop(baseline, errors='ignore')
    if on_conditions.empty:
        print(f"Warning: No 'ON' conditions found to compare against baseline for hand '{hand}'.")
        return results

    baseline_series = summary_df.loc[baseline]
    raw_change_df = summary_df.loc[on_conditions].subtract(baseline_series, axis=1)
    
    improvement_df = raw_change_df.copy()
    for param, direction in parameter_directions.items():
        if param in improvement_df.columns and direction == 'lower':
            improvement_df[param] *= -1
    results['improvement_df'] = improvement_df

    responsiveness_scores = improvement_df.std().fillna(0)
    responsiveness_scores = responsiveness_scores[responsiveness_scores > 1e-9] # Filter out non-variable params
    results['responsiveness_scores'] = responsiveness_scores

    if responsiveness_scores.empty or responsiveness_scores.sum() == 0:
        print(f"Warning: No responsive parameters found for hand '{hand}'. Cannot calculate dynamic scores.")
        return results

    # Implement Regularized Dynamic Weighting
    data_driven_weights = responsiveness_scores / responsiveness_scores.sum()
    n_responsive_params = len(data_driven_weights)
    uniform_weights = pd.Series(1.0 / n_responsive_params, index=data_driven_weights.index)
    
    final_dynamic_weights = (1 - shrinkage_lambda) * data_driven_weights + shrinkage_lambda * uniform_weights
    results['final_dynamic_weights'] = final_dynamic_weights

    # Calculate the final Dynamically Weighted Improvement Score (DWIS)
    common_params = improvement_df.columns.intersection(final_dynamic_weights.index)
    dynamic_scores = improvement_df[common_params].dot(final_dynamic_weights[common_params])
    results['dynamic_scores'] = dynamic_scores
    
    # Rank conditions based on the DWIS
    ranked_scores = dynamic_scores.sort_values(ascending=False)
    results['dynamic_ranking_results'] = {
        'ranked_names': ranked_scores.index.tolist(),
        'ranked_scores': ranked_scores.values.tolist(),
    }
    
    return results