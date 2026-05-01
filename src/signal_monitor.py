import numpy as np
import pandas as pd
from dataclasses import dataclass

CN0_THRESHOLD = 32.0
MIN_SVS = 4
GAP_S = 90

@dataclass
class MonitoringResult:
    availability_pct: dict
    cn0_stats: pd.DataFrame
    anomalies: pd.DataFrame
    gaps: pd.DataFrame
    epoch_stats: pd.DataFrame
    summary_status: str
    galileo_gps_delta: float

def compute_availability(df):
    total = df["epoch"].nunique()
    result = {}
    for const in df["constellation"].unique():
        valid = df[(df["constellation"] == const) & df["valid"]]
        per_epoch = valid.groupby("epoch")["sv"].nunique()
        available = (per_epoch >= MIN_SVS).sum()
        result[const] = round(100.0 * available / total, 2)
    return result

def compute_cn0_stats(df):
    valid = df[df["valid"]].copy()
    valid["elev_band"] = pd.cut(valid["elevation"], bins=[0, 20, 40, 90],
                               labels=["Low (0-20deg)", "Mid (20-40deg)", "High (>40deg)"])
    return valid.groupby(["constellation", "elev_band"])["cn0"].agg(
        count="count", mean="mean", std="std",
        p5=lambda x: x.quantile(0.05)).round(2)

def detect_anomalies(df):
    valid = df[df["valid"]].copy()
    anom = valid[valid["cn0"] < CN0_THRESHOLD].copy()
    anom["type"] = "Low C/N0"
    anom["severity"] = np.where(anom["cn0"] < 28, "SEVERE", "MODERATE")
    return anom.reset_index(drop=True)

def detect_tracking_gaps(df):
    gaps = []
    for sv, grp in df[df["valid"]].groupby("sv"):
        grp = grp.sort_values("epoch")
        diffs = grp["epoch"].diff().dt.total_seconds()
        mask = diffs > GAP_S
        for epoch, gap_s in zip(grp["epoch"][mask], diffs[mask]):
            gaps.append({"sv": sv, "epoch": epoch, "gap_s": round(gap_s, 0),
                         "constellation": grp["constellation"].iloc[0]})
    return pd.DataFrame(gaps) if gaps else pd.DataFrame(
        columns=["sv", "epoch", "gap_s", "constellation"])

def compute_epoch_stats(df):
    return df[df["valid"]].groupby(["epoch", "constellation"]).agg(
        sv_count=("sv", "nunique"),
        mean_cn0=("cn0", "mean"),
        min_elev=("elevation", "min")).reset_index()

def run_monitoring(df):
    availability = compute_availability(df)
    cn0_stats = compute_cn0_stats(df)
    anomalies = detect_anomalies(df)
    gaps = detect_tracking_gaps(df)
    epoch_stats = compute_epoch_stats(df)
    gal = availability.get("Galileo", 0)
    status = "NOMINAL" if gal >= 99 else ("DEGRADED" if gal >= 95 else "CRITICAL")
    valid = df[df["valid"]]
    delta = round(valid[valid["constellation"]=="Galileo"]["cn0"].mean() -
                  valid[valid["constellation"]=="GPS"]["cn0"].mean(), 2)
    return MonitoringResult(availability_pct=availability, cn0_stats=cn0_stats,
        anomalies=anomalies, gaps=gaps, epoch_stats=epoch_stats,
        summary_status=status, galileo_gps_delta=delta)
