"""
Example usage of Somatosensory Jitter Single Fiber EMG (SFEMG) Skill.
Standard library only, zero mock.
"""

from client import SomatosensorySFEMGJitterClient


def run_demo():
    print("=== Somatosensory SFEMG Jitter Skill Demo ===")

    # Initialize client for Extensor Digitorum Communis (EDC)
    client = SomatosensorySFEMGJitterClient(target_muscle="extensor_digitorum_communis")

    # 1. Single pair evaluation with physiological microsecond jitter
    # Normal physiological jitter in EDC is typically 15-35 us
    normal_series = [
        1250.0, 1262.5, 1245.0, 1270.0, 1255.0,
        1248.0, 1265.0, 1252.0, 1258.0, 1249.0,
        1263.0, 1251.0, 1268.0, 1244.0, 1257.0
    ]
    pair_res = client.compute_single_pair_jitter(normal_series, blocked_discharges=0)
    print("\n--- Single Pair Jitter Result ---")
    print(f"Mean IPI: {pair_res['mean_ipi_us']} us")
    print(f"MCD: {pair_res['mcd_us']} us | MSD: {pair_res['msd_us']} us")
    print(f"Drift Detected: {pair_res['drift_detected']} (Ratio: {pair_res['drift_ratio']})")
    print(f"Effective Jitter: {pair_res['effective_jitter_us']} us (Pair Limit: {pair_res['pair_limit_us']} us)")
    print(f"Pair Status: {'Abnormal' if pair_res['is_abnormal'] else 'Normal'}")

    # 2. Multi-pair clinical study simulation (representing neuromuscular transmission assessment)
    study_records = [
        {"ipi_series_us": [1200 + i * 2 + (i % 3) * 15 for i in range(12)], "blocked_discharges": 0},
        {"ipi_series_us": [1150 + (i % 2) * 20 for i in range(12)], "blocked_discharges": 0},
        {"ipi_series_us": [1300 + (i % 4) * 25 for i in range(12)], "blocked_discharges": 0},
        {"ipi_series_us": [980 + (i % 2) * 18 for i in range(12)], "blocked_discharges": 0},
        {"ipi_series_us": [1400 + (i % 3) * 65 for i in range(12)], "blocked_discharges": 1},  # elevated pair with blocking
    ]

    study_res = client.evaluate_multi_pair_study(study_records)
    print("\n--- Multi-Pair Study Clinical Evaluation ---")
    print(f"Muscle Analyzed: {study_res['muscle_analyzed']}")
    print(f"Total Pairs: {study_res['total_pairs_analyzed']}")
    print(f"Mean Study Jitter: {study_res['mean_study_jitter_us']} us (Mean Normal Limit: {study_res['reference_mean_limit_us']} us)")
    print(f"Abnormal Pairs: {study_res['abnormal_pairs_count']} ({study_res['abnormal_pairs_pct']}%)")
    print(f"Total Blocked Discharges: {study_res['total_blocked_discharges']}")
    print(f"Safety Margin Index: {study_res['safety_margin_index']}")
    print(f"Classification: {study_res['diagnostic_classification']} ({study_res['severity_grade']})")


if __name__ == "__main__":
    run_demo()
