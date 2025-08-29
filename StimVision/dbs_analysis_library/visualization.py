# --- REFINED FILE: dbs_analysis_library/visualization.py ---

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive visualization library for generating publication-quality plots
for both individual patient reports and group-level analyses.
"""
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import seaborn as sns
from .analysis import perform_full_hand_analysis
from .utils import VARIABLE_NAMES

def set_publication_style():
    """Sets a consistent, publication-quality style for all matplotlib plots."""
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica'], 'font.size': 16,
        'axes.titlesize': 20, 'axes.labelsize': 18, 'xtick.labelsize': 14, 'ytick.labelsize': 14,
        'legend.fontsize': 14, 'figure.titlesize': 24, 'figure.dpi': 300,
        'savefig.format': 'pdf', 'savefig.bbox': 'tight',
    })

# --- I. Individual Patient Report Visualization ---

def _plot_engineering_view(ax, improvement_df, best_program_name=None):
    """
    Plots the standard "Engineering View" heatmap, with conditions sorted
    chronologically and the baseline forced to the bottom.
    """
    plot_df = improvement_df.copy()
    plot_df.columns = plot_df.columns.map(lambda x: VARIABLE_NAMES.get(x, x))
    
    baseline_name = next((idx for idx in plot_df.index if "dbs off" in idx.lower()), None)
    
    if baseline_name:
        baseline_row = plot_df.loc[[baseline_name]]
        other_rows = plot_df.drop(baseline_name).sort_index()
        final_df = pd.concat([other_rows, baseline_row])
    else:
        final_df = plot_df.sort_index()

    limit = np.nanmax(np.abs(final_df.to_numpy())); limit = limit if limit > 1e-6 else 0.1
    sns.heatmap(final_df, ax=ax, cmap='PRGn', vmin=-limit, vmax=limit, cbar=False)
    ax.set_title("(A) Standard \"Engineering View\"", pad=20)
    ax.set_xlabel("Kinematic Parameters")
    ax.set_ylabel("Conditions (Chronological)")
    ax.tick_params(axis='x', labelrotation=90)
    
    if best_program_name and best_program_name in final_df.index:
        best_idx = final_df.index.get_loc(best_program_name)
        ax.add_patch(plt.Rectangle((0, best_idx), final_df.shape[1], 1, lw=3, ec='gold', fc='none'))

def _plot_dynamic_clinical_view(ax, improvement_df, responsiveness_scores, ranked_conditions):
    """
    Plots the sorted "Dynamic Clinical View" heatmap, with parameters sorted by
    responsiveness and conditions sorted by overall improvement score.
    """
    sorted_params = responsiveness_scores.sort_values(ascending=False).index
    plot_df = improvement_df[sorted_params].copy()
    plot_df.columns = plot_df.columns.map(lambda x: VARIABLE_NAMES.get(x, x))
    
    baseline_name = next((idx for idx in plot_df.index if "dbs off" in idx.lower()), None)

    if baseline_name:
        baseline_row = plot_df.loc[[baseline_name]]
        other_conditions_ranked = [cond for cond in ranked_conditions if cond != baseline_name]
        sorted_other = plot_df.loc[other_conditions_ranked]
        final_df = pd.concat([sorted_other, baseline_row])
    else:
        final_df = plot_df.reindex(ranked_conditions)

    limit = np.nanmax(np.abs(final_df.to_numpy())); limit = limit if limit > 1e-6 else 0.1
    sns.heatmap(final_df, ax=ax, cmap='PRGn', vmin=-limit, vmax=limit, cbar_kws={'label': 'Improvement Score'})
    ax.set_title("(B) Dynamic \"Clinical View\"", pad=20)
    ax.set_xlabel("Kinematic Parameters (by Responsiveness)")
    ax.set_ylabel("Conditions (by Overall Score)")
    ax.tick_params(axis='x', labelrotation=90)

def create_ismr_patient_report(patient_id, data_by_condition, baseline, output_folder, default_lambda=0.1):
    """
    Generates and saves a standardized Engineering vs. Clinical View plot for a
    single patient, using the right hand by default for visualization.
    """
    print(f"--- Generating visual report for patient {patient_id} ---")
    
    plot_results = perform_full_hand_analysis(data_by_condition, "Right", baseline, shrinkage_lambda=default_lambda)
    if plot_results['improvement_df'].empty:
        print(f"Warning: Could not generate report for {patient_id}. No improvement data found for right hand.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(24, 10), constrained_layout=True)
    fig.suptitle(f"Patient Report: {patient_id} (Baseline: {baseline})", fontsize=22)
    
    best_program = plot_results['dynamic_ranking_results']['ranked_names'][0] if plot_results['dynamic_ranking_results']['ranked_names'] else None
    _plot_engineering_view(axes[0], plot_results['improvement_df'], best_program)

    ranked_conditions = plot_results['dynamic_ranking_results']['ranked_names']
    _plot_dynamic_clinical_view(axes[1], plot_results['improvement_df'], plot_results['responsiveness_scores'], ranked_conditions)

    save_path = os.path.join(output_folder, f"report_{patient_id}_engineering_vs_clinical.pdf")
    plt.savefig(save_path)
    plt.close(fig)
    print(f"Successfully saved patient report to: {save_path}")

# --- II. Group-Level Analysis Visualization ---

def plot_group_box_and_bar(data_df, label_suffix, output_dir, plot_title_prefix):
    """Generates and saves group-level box and bar plots for a given metric."""
    n_patients, n_parameters = data_df.shape
    if n_parameters == 0: return

    # Box plots of distribution
    plt.figure(figsize=(max(15, int(n_parameters * 0.7)), 8))
    sns.boxplot(data=data_df, palette="viridis")
    plt.title(f"{plot_title_prefix} Distribution {label_suffix} (n={n_patients})")
    plt.ylabel(f"{plot_title_prefix} Score")
    plt.xticks(rotation=90, ha="right")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(output_dir, f"group_boxplot_{plot_title_prefix.lower().replace(' ','_')}_{label_suffix.strip('()')}.pdf"))
    plt.close()

    # Bar chart of mean with Standard Error of the Mean (SEM)
    mean_scores = data_df.mean().sort_values(ascending=False)
    sem_scores = data_df.sem().reindex(mean_scores.index)
    plt.figure(figsize=(max(15, int(n_parameters * 0.7)), 8))
    mean_scores.plot(kind='bar', yerr=sem_scores, capsize=4, color='skyblue', edgecolor='black')
    plt.title(f"Mean {plot_title_prefix} {label_suffix} (n={n_patients}, +/- SEM)")
    plt.ylabel(f"Mean {plot_title_prefix} Score")
    plt.xticks(rotation=90, ha="right")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(output_dir, f"group_barchart_{plot_title_prefix.lower().replace(' ','_')}_{label_suffix.strip('()')}.pdf"))
    plt.close()