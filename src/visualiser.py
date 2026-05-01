import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from pathlib import Path

COLORS = {"Galileo": "#003087", "GPS": "#D4A017"}

def plot_dashboard(df, result, output_dir="results"):
    Path(output_dir).mkdir(exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle("Galileo / GPS Signal Quality Monitor", fontsize=13, fontweight="bold")
    ep = result.epoch_stats
    ax = axes[0, 0]
    for c, col in COLORS.items():
        d = ep[ep["constellation"] == c]
        ax.plot(d["epoch"], d["sv_count"], color=col, lw=1.3, label=c)
    ax.axhline(4, color="red", ls="--", lw=0.9, label="Min 4 SVs")
    ax.set_title("Valid Satellite Count", fontsize=10, fontweight="bold")
    ax.set_ylabel("Satellites"); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax = axes[0, 1]
    for c, col in COLORS.items():
        d = ep[ep["constellation"] == c]
        ax.plot(d["epoch"], d["mean_cn0"], color=col, lw=1.3, label=c)
    ax.axhline(32, color="orange", ls="--", lw=0.9, label="Anomaly threshold")
    ax.set_title("Mean C/N0 per Epoch", fontsize=10, fontweight="bold")
    ax.set_ylabel("C/N0 (dB-Hz)"); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax = axes[1, 0]
    valid = df[df["valid"]]
    for c, col in COLORS.items():
        sub = valid[valid["constellation"] == c].sample(min(600, len(valid[valid["constellation"]==c])), random_state=42)
        ax.scatter(sub["elevation"], sub["cn0"], alpha=0.2, s=7, color=col, label=c)
    elev_r = np.linspace(10, 85, 50)
    ax.plot(elev_r, 44.5 + 0.32 * elev_r, "b--", lw=1, label="Galileo model", alpha=0.6)
    ax.set_title("C/N0 vs Elevation", fontsize=10, fontweight="bold")
    ax.set_xlabel("Elevation (deg)"); ax.set_ylabel("C/N0 (dB-Hz)")
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
    ax = axes[1, 1]
    if len(result.anomalies) > 0:
        for c, col in COLORS.items():
            sub = result.anomalies[result.anomalies["constellation"] == c]
            if len(sub): ax.scatter(sub["epoch"], sub["cn0"], s=18, color=col, alpha=0.7, label=c)
    ax.axhline(32, color="red", ls="--", lw=0.9, label="Threshold 32 dB-Hz")
    ax.set_title("Anomaly Events", fontsize=10, fontweight="bold")
    ax.set_ylabel("C/N0 (dB-Hz)"); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.tight_layout()
    out = output_dir + "/monitoring_dashboard.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print("Dashboard saved: " + out)
