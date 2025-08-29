# --- REFINED FILE: dbs_analysis_library/utils.py ---

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared constants, parameter mappings, and utility functions for the DBS analysis project.
"""
import numpy as np

# Defines whether a higher or lower value indicates clinical improvement.
parameter_directions = {
    "MeanAmplitude": "higher", "StdAmplitude": "lower",
    "MeanSpeed": "higher", "StdSpeed": "lower",
    "MeanRMSVelocity": "higher", "StdRMSVelocity": "lower",
    "MeanOpeningSpeed": "higher", "StdOpeningSpeed": "lower",
    "MeanClosingSpeed": "higher", "StdClosingSpeed": "lower",
    "MeanCycleDuration": "lower", "StdCycleDuration": "lower",
    "RangeCycleDuration": "lower", "Frequency": "higher",
    "AmplitudeDecay": "lower", "VelocityDecay": "lower",
    "RateDecay": "lower", "CVAmplitude": "lower",
    "CVCycleDuration": "lower", "CVSpeed": "lower",
    "CVRMSVelocity": "lower", "CVOpeningSpeed": "lower",
    "CVClosingSpeed": "lower"
}

# Mapping from standardized parameter names to human-readable names for plots.
VARIABLE_NAMES = {
    'MeanAmplitude': 'Mean Amplitude', 'StdAmplitude': 'SD of Amplitude',
    'MeanSpeed': 'Mean Speed', 'StdSpeed': 'SD of Speed',
    'MeanRMSVelocity': 'Mean RMS Velocity', 'StdRMSVelocity': 'SD of RMS Velocity',
    'MeanOpeningSpeed': 'Mean Opening Speed', 'StdOpeningSpeed': 'SD of Opening Speed',
    'MeanClosingSpeed': 'Mean Closing Speed', 'StdClosingSpeed': 'SD of Closing Speed',
    'MeanCycleDuration': 'Mean Cycle Duration', 'StdCycleDuration': 'SD of Cycle Duration',
    'RangeCycleDuration': 'Range of Cycle Duration', 'Frequency': 'Frequency',
    'AmplitudeDecay': 'Amplitude Decay', 'VelocityDecay': 'Velocity Decay',
    'RateDecay': 'Rate Decay', 'CVAmplitude': 'CV of Amplitude',
    'CVCycleDuration': 'CV of Cycle Duration', 'CVSpeed': 'CV of Speed',
    'CVRMSVelocity': 'CV of RMS Velocity', 'CVOpeningSpeed': 'CV of Opening Speed',
    'CVClosingSpeed': 'CV of Closing Speed'
}

def tuckers_congruence_coefficient(vec1, vec2):
    """Calculates Tucker's Congruence Coefficient (Phi) between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    if norm_product == 0:
        return 0.0
    return dot_product / norm_product