import numpy as np
import pandas as pd
from datetime import datetime, timedelta

GALILEO_SVS = ["E01","E02","E03","E04","E05","E07","E08","E09",
               "E11","E12","E14","E18","E19","E21","E24","E25",
               "E26","E27","E30","E31","E33","E36"]
GPS_SVS = ["G01","G03","G06","G07","G09","G11","G14","G17",
           "G19","G21","G22","G25","G28","G30","G31","G32"]

def generate(duration_hours=6, sampling_rate_s=30, inject_events=True, seed=42):
    np.random.seed(seed)
    n = int(duration_hours * 3600 / sampling_rate_s)
    t0 = datetime(2026, 4, 27, 8, 0, 0)
    epochs = [t0 + timedelta(seconds=i * sampling_rate_s) for i in range(n)]
    records = []
    for sv in GALILEO_SVS + GPS_SVS:
        is_gal = sv.startswith("E")
        const = "Galileo" if is_gal else "GPS"
        base = 44.5 if is_gal else 42.5
        ps = np.random.randint(0, n // 3)
        pe = min(ps + np.random.randint(n // 3, int(n * 0.9)), n)
        sz = pe - ps
        me = np.random.uniform(25, 85)
        t = np.linspace(0, 3.14159, sz)
        elevs = np.maximum(5.0, me * np.sin(t) + np.random.normal(0, 0.3, sz))
        azims = np.linspace(np.random.uniform(0, 180), np.random.uniform(180, 360), sz)
        for j, i in enumerate(range(ps, pe)):
            elev = elevs[j]
            cn0 = base + 0.32 * elev + np.random.normal(0, 1.8)
            if inject_events:
                if 100 <= i <= 104 and sv in ["E01","E03","G07"]:
                    cn0 -= np.random.uniform(6, 12)
                if elev < 20 and np.random.random() < 0.08:
                    cn0 -= np.random.uniform(2, 7)
                if 300 <= i <= 315:
                    cn0 += np.random.normal(-1.5, 2.0)
            cn0 = max(18.0, round(cn0, 2))
            records.append({"epoch": epochs[i], "sv": sv, "constellation": const,
                "cn0": cn0, "elevation": round(elev, 2),
                "azimuth": round(azims[j] % 360, 1), "valid": elev >= 10 and cn0 >= 30})
    return pd.DataFrame(records)
