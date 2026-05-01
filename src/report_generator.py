from datetime import datetime
from pathlib import Path

def generate_text_report(df, result, station="Synthetic", output_dir="results"):
    sep = "=" * 72
    lines = [sep,
        "GNSS SIGNAL QUALITY MONITORING REPORT",
        "Galileo / GPS Multi-Constellation Performance Analysis",
        "Station     : " + station,
        "Generated   : " + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "Window      : " + str(df["epoch"].min()) + " to " + str(df["epoch"].max()),
        sep, "",
        "[1] SERVICE AVAILABILITY (>= 4 valid satellites)"]
    for const, avail in result.availability_pct.items():
        s = "OK" if avail >= 99 else ("WARN" if avail >= 95 else "CRIT")
        lines.append("  " + const.ljust(10) + str(avail).rjust(7) + "%   [" + s + "]")
    lines += ["", "[2] SIGNAL QUALITY - C/N0 Statistics"]
    lines.append(result.cn0_stats.to_string())
    n = len(result.anomalies)
    lines += ["", "[3] ANOMALIES DETECTED (threshold: 32 dB-Hz)",
              "  Total events: " + str(n)]
    if n > 0:
        lines.append("  Affected SVs: " + ", ".join(sorted(result.anomalies["sv"].unique())))
    lines += ["", "[4] SIGNAL CONTINUITY",
              "  Tracking gaps: " + str(len(result.gaps))]
    lines += ["", "[5] MULTI-SYSTEM COMPARISON",
              "  Galileo - GPS C/N0 delta: " + str(result.galileo_gps_delta) + " dB-Hz"]
    lines += ["", "[6] SUMMARY",
              "  Galileo Service Status: " + result.summary_status, "", sep]
    report = "\n".join(lines)
    Path(output_dir).mkdir(exist_ok=True)
    with open(output_dir + "/monitoring_report.txt", "w") as f:
        f.write(report)
    print(report)
