---
name: genpark-personal-agent-somatosensory-jitter-single-fiber-emg-sfemg-skill
description: Precision neuromuscular transmission safety margin evaluation and jitter calculation using Single Fiber Electromyography (SFEMG).
---

# Somatosensory Jitter Single Fiber EMG (SFEMG) Skill

## Overview
Computes Mean Consecutive Difference (MCD), Mean Sorted Difference (MSD), jitter drift correction, and impulse blocking rates for clinical assessment of the neuromuscular junction (NMJ). Standard library only, zero external dependencies.

## Key Capabilities
- **Single Pair Analysis**: Calculates consecutive and sorted interpotential interval variances (MCD/MSD) with automatic firing frequency drift compensation.
- **Impulse Blocking Quantification**: Tracks transmission failure percentages across individual pairs and complete clinical multi-pair protocols.
- **Clinical Multi-Pair Study**: Evaluates diagnostic thresholds for neuromuscular junction failure (e.g. Myasthenia Gravis, Lambert-Eaton syndrome) across anatomical muscle groups.

## Reference Limits
- **Extensor Digitorum Communis (EDC)**: Pair limit 55.0 µs, Mean limit 34.0 µs
- **Frontalis**: Pair limit 45.0 µs, Mean limit 30.0 µs
- **Orbicularis Oculi**: Pair limit 45.0 µs, Mean limit 32.0 µs
