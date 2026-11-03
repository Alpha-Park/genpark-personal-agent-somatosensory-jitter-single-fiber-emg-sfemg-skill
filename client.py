"""
Somatosensory Jitter Single Fiber EMG (SFEMG) Skill Client.
Standard library only, zero mock, deterministic mathematical and neurophysiological computation.
"""

from typing import Dict, Any, List, Optional
import math


class SomatosensorySFEMGJitterClient:
    """
    Precision client for neuromuscular transmission analysis using Single Fiber Electromyography (SFEMG).
    Computes Mean Consecutive Difference (MCD), Mean Sorted Difference (MSD), jitter drift correction,
    impulse blocking rates, and neuromuscular junction (NMJ) transmission safety factors.
    """

    # Reference upper limits for individual pairs and mean MCD (in microseconds, us)
    MUSCLE_REFERENCE_LIMITS = {
        "extensor_digitorum_communis": {"pair_limit_us": 55.0, "mean_limit_us": 34.0},
        "frontalis": {"pair_limit_us": 45.0, "mean_limit_us": 30.0},
        "orbicularis_oculi": {"pair_limit_us": 45.0, "mean_limit_us": 32.0},
        "biceps_brachii": {"pair_limit_us": 40.0, "mean_limit_us": 25.0},
        "tibialis_anterior": {"pair_limit_us": 55.0, "mean_limit_us": 35.0},
        "generic": {"pair_limit_us": 50.0, "mean_limit_us": 33.0}
    }

    def __init__(self, target_muscle: str = "extensor_digitorum_communis"):
        muscle_key = target_muscle.lower().replace(" ", "_")
        self.target_muscle = muscle_key if muscle_key in self.MUSCLE_REFERENCE_LIMITS else "generic"
        self.limits = self.MUSCLE_REFERENCE_LIMITS[self.target_muscle]

    def compute_single_pair_jitter(
        self,
        ipi_series_us: List[float],
        blocked_discharges: int = 0
    ) -> Dict[str, Any]:
        """
        Calculates MCD, MSD, and blocking percentage for a single neuromuscular potential pair.
        
        Args:
            ipi_series_us: List of consecutive interpotential intervals in microseconds (us). Minimum 10 intervals.
            blocked_discharges: Number of blocked transmissions observed during the recording series.
            
        Returns:
            Dict containing MCD, MSD, effective jitter, blocking percentage, and pair normality flag.
        """
        if not ipi_series_us or len(ipi_series_us) < 10:
            raise ValueError("SFEMG requires at least 10 consecutive interpotential intervals (IPIs) per pair.")

        n = len(ipi_series_us)
        total_discharges = n + blocked_discharges

        # Mean Consecutive Difference (MCD):
        diffs = [abs(ipi_series_us[i + 1] - ipi_series_us[i]) for i in range(n - 1)]
        mcd = sum(diffs) / (n - 1)

        # Mean Sorted Difference (MSD) for drift elimination:
        sorted_ipi = sorted(ipi_series_us)
        msd_diffs = [abs(sorted_ipi[i + 1] - sorted_ipi[i]) for i in range(n - 1)]
        msd = sum(msd_diffs) / (n - 1)

        # Drift correction rule: if MCD / MSD > 1.25, slow trend drift is present; MSD provides true jitter
        drift_ratio = mcd / msd if msd > 0 else 1.0
        drift_detected = drift_ratio > 1.25
        effective_jitter_us = msd if drift_detected else mcd

        blocking_rate_pct = (blocked_discharges / total_discharges) * 100.0 if total_discharges > 0 else 0.0
        pair_abnormal = (effective_jitter_us > self.limits["pair_limit_us"]) or (blocking_rate_pct > 0.0)

        return {
            "interval_count": n,
            "mean_ipi_us": round(sum(ipi_series_us) / n, 2),
            "mcd_us": round(mcd, 2),
            "msd_us": round(msd, 2),
            "drift_ratio": round(drift_ratio, 3),
            "drift_detected": drift_detected,
            "effective_jitter_us": round(effective_jitter_us, 2),
            "blocked_discharges": blocked_discharges,
            "total_discharges": total_discharges,
            "blocking_rate_pct": round(blocking_rate_pct, 2),
            "pair_limit_us": self.limits["pair_limit_us"],
            "is_abnormal": pair_abnormal
        }

    def evaluate_multi_pair_study(
        self,
        pair_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates a complete SFEMG clinical examination across multiple motor unit pairs (typically 20 pairs).
        
        Args:
            pair_records: List of dicts, each with 'ipi_series_us' (list) and optional 'blocked_discharges' (int).
            
        Returns:
            Dict containing multi-pair summary, percentage of abnormal pairs, overall mean MCD,
            diagnostic classification (Normal, Borderline, Abnormal), and NMJ safety margin.
        """
        if not pair_records or len(pair_records) < 5:
            raise ValueError("A reliable SFEMG study requires at least 5 pairs (standard clinical target is 20 pairs).")

        analyzed_pairs = []
        abnormal_pairs_count = 0
        total_blocked_events = 0
        all_effective_jitters = []

        for idx, rec in enumerate(pair_records):
            series = rec.get("ipi_series_us", [])
            blocked = rec.get("blocked_discharges", 0)
            res = self.compute_single_pair_jitter(series, blocked)
            res["pair_index"] = idx + 1
            analyzed_pairs.append(res)
            
            all_effective_jitters.append(res["effective_jitter_us"])
            if res["is_abnormal"]:
                abnormal_pairs_count += 1
            total_blocked_events += res["blocked_discharges"]

        total_pairs = len(analyzed_pairs)
        mean_study_jitter_us = sum(all_effective_jitters) / total_pairs
        abnormal_pairs_pct = (abnormal_pairs_count / total_pairs) * 100.0

        mean_limit = self.limits["mean_limit_us"]
        pair_limit = self.limits["pair_limit_us"]

        # Clinical Diagnostic Criteria:
        # Abnormal if: > 10% of pairs have jitter > pair_limit, OR mean jitter > mean_limit, OR blocking present.
        has_blocking = total_blocked_events > 0
        mean_exceeded = mean_study_jitter_us > mean_limit
        pairs_exceeded = abnormal_pairs_pct > 10.0

        if pairs_exceeded or mean_exceeded or has_blocking:
            if abnormal_pairs_pct >= 50.0 or total_blocked_events >= 5:
                diagnostic_classification = "Severe Neuromuscular Junction Dysfunction"
                severity_grade = "Severe"
            elif abnormal_pairs_pct >= 25.0 or total_blocked_events > 0:
                diagnostic_classification = "Moderate Neuromuscular Transmission Failure"
                severity_grade = "Moderate"
            else:
                diagnostic_classification = "Mild Defect of Neuromuscular Transmission"
                severity_grade = "Mild"
            is_pathological = True
        elif abnormal_pairs_pct > 5.0 or (mean_study_jitter_us > mean_limit * 0.92):
            diagnostic_classification = "Borderline Neuromuscular Transmission"
            severity_grade = "Borderline"
            is_pathological = False
        else:
            diagnostic_classification = "Normal Neuromuscular Transmission"
            severity_grade = "Normal"
            is_pathological = False

        # NMJ safety margin index (higher is safer, 1.0 is threshold)
        safety_margin_index = round(mean_limit / max(mean_study_jitter_us, 1.0), 3)

        return {
            "muscle_analyzed": self.target_muscle,
            "total_pairs_analyzed": total_pairs,
            "abnormal_pairs_count": abnormal_pairs_count,
            "abnormal_pairs_pct": round(abnormal_pairs_pct, 1),
            "mean_study_jitter_us": round(mean_study_jitter_us, 2),
            "reference_mean_limit_us": mean_limit,
            "reference_pair_limit_us": pair_limit,
            "total_blocked_discharges": total_blocked_events,
            "has_blocking": has_blocking,
            "safety_margin_index": safety_margin_index,
            "diagnostic_classification": diagnostic_classification,
            "severity_grade": severity_grade,
            "is_pathological": is_pathological,
            "pairs_detail": analyzed_pairs
        }
