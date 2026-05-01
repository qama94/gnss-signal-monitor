# Galileo / GPS Signal Quality Monitor

A Python tool for monitoring GNSS signal quality and service performance,
built around the operational methodology of the
[Galileo Reference Centre (GRC)](https://www.gsc-europa.eu/galileo/services/galileo-reference-centre)
in Noordwijk, Netherlands.

The GRC's mission is to independently monitor Galileo signal quality and
service performance, comparing it against GPS, GLONASS, and BeiDou.
This project replicates the core monitoring workflows at that level.

---

## What it does

| Metric | Description |
|--------|-------------|
| **Service availability** | % of epochs with ≥ 4 valid satellites per constellation |
| **C/N0 statistics** | Mean, std, 5th percentile by constellation and elevation band |
| **Anomaly detection** | Low signal events (< 32 dB-Hz), classified by severity |
| **Signal continuity** | Tracking gap detection (> 3× nominal sample rate) |
| **Multi-system comparison** | Galileo vs GPS C/N0 performance delta |

Outputs:
- Structured monitoring report (plain text, GRC-style format)
- 4-panel dashboard: satellite count, mean C/N0, C/N0 vs elevation, anomaly timeline

---

## Project structure

```
gnss-signal-monitor/
├── main.py                    # Entry point — run this
├── src/
│   ├── signal_monitor.py      # Core metrics and anomaly detection
│   ├── data_generator.py      # Realistic synthetic data (calibrated to Galileo E1 OS)
│   ├── rinex_parser.py        # RINEX 3 parser for real IGS observation files
│   ├── visualiser.py          # 4-panel monitoring dashboard
│   └── report_generator.py   # Structured monitoring report
├── results/                   # Generated outputs (dashboard, report)
├── data/sample/               # Place real RINEX files here
├── docs/                      # Background on GNSS monitoring methodology
├── requirements.txt
└── README.md
```

---

## Quick start

```bash
# Clone and install
git clone https://github.com/qama94/gnss-signal-monitor.git
cd gnss-signal-monitor
pip install -r requirements.txt

# Run with synthetic data (no RINEX file needed)
python main.py

# Run with a real RINEX 3 observation file
python main.py --rinex data/sample/WSRT00NLD_R_20261150000_01D_30S_MO.rnx

# Show all options
python main.py --help
```

---

## Using real GNSS data

Real RINEX observation files are freely available from the
[IGS](https://www.igs.org/) network via:

| Source | URL |
|--------|-----|
| BKG (Germany) | https://igs.bkg.bund.de/root_ftp/IGS/obs/YYYY/DDD/ |
| CDDIS (NASA) | https://cddis.nasa.gov/archive/gnss/data/daily/ |
| IGN (France) | https://igs.ign.fr/pub/igs/data/ |

**Recommended European stations** (include Galileo observations):

| Station | Country | Code |
|---------|---------|------|
| Westerbork | Netherlands | WSRT |
| Brussels | Belgium | BRUX |
| Warnemünde | Germany | WARN |
| Onsala | Sweden | ONSA |
| Zimmerwald | Switzerland | ZIMM |

**Download example:**
```bash
# Download WSRT station, day 115 of 2026
wget https://igs.bkg.bund.de/root_ftp/IGS/obs/2026/115/wsrt1150.26o.gz
gunzip wsrt1150.26o.gz
python main.py --rinex wsrt1150.26o
```

> IGS files are often Hatanaka-compressed (.crx). Decompress with:
> `pip install hatanaka` then `hatanaka.decompress_on_disk('file.crx')`

---

## Monitoring dashboard

Running `python main.py` generates `results/monitoring_dashboard.png`:

![Monitoring Dashboard](results/monitoring_dashboard.png)

Four panels:
1. **Satellite count** — valid SVs per epoch per constellation, vs minimum threshold (4)
2. **Mean C/N0** — signal strength over time, with anomaly threshold line
3. **C/N0 vs elevation** — scatter plot with theoretical Galileo E1 model overlay
4. **Anomaly events** — low C/N0 epochs, colour-coded by constellation and severity

---

## Sample monitoring report

```
========================================================================
GNSS SIGNAL QUALITY MONITORING REPORT
Multi-Constellation Performance Analysis — Galileo / GPS
Station     : WSRT (Westerbork, NL)
Generated   : 2026-04-27 14:00:00 UTC
Window      : 2026-04-27 08:00 – 14:00 UTC  (6.0 h)
Epochs      : 714 × 30 s
========================================================================

[1] SERVICE AVAILABILITY (>= 4 valid satellites)
  Galileo     99.16%   [OK]
  GPS         97.48%   [OK]

[2] SIGNAL QUALITY — C/N0 by Constellation and Elevation Band
                              count   mean   std     p5
  Galileo  Low (0-20deg)     1578   48.98  2.38  44.93
           Mid (20-40deg)    3923   53.94  2.60  49.73
           High (>40deg)     3503   63.59  4.40  56.79
  GPS      Low (0-20deg)      769   46.94  2.30  42.98
           ...

[3] ANOMALIES DETECTED  (threshold: 32 dB-Hz)
  Total events      : 3
  Affected SVs      : E01, E03, G07
  Severity MODERATE : 3

[5] MULTI-SYSTEM COMPARISON
  Galileo – GPS C/N0 delta : +2.05 dB-Hz

[6] SUMMARY ASSESSMENT
  Galileo Service Status   : NOMINAL
========================================================================
```

---

## Signal quality model

C/N0 is modelled as a function of elevation angle, calibrated against
EUSPA Galileo Open Service Performance Assessment data:

```
C/N0(elev) = C/N0_zenith + k × elev + ε
```

Where:
- `C/N0_zenith` = 44.5 dB-Hz (Galileo E1 OS), 42.5 dB-Hz (GPS L1 C/A)
- `k` = 0.32 dB-Hz/degree
- `ε` ~ N(0, 1.8) dB-Hz

The model is overlaid on the scatter plot in Panel 3 for visual validation.

---

## Roadmap

- [ ] Grafana-compatible JSON metrics export
- [ ] Alert system for threshold violations (email/webhook)
- [ ] Multi-station network monitoring
- [ ] Navigation file integration for elevation angle computation from position
- [ ] GLONASS and BeiDou support
- [ ] Time series anomaly detection using statistical process control

---

## References

- EUSPA, *Galileo Open Service Performance Assessment*, 2024
- IGS, *RINEX 3 Observation Data Format*, v3.05
- B. Hofmann-Wellenhof et al., *GNSS — Global Navigation Satellite Systems*, 2008
- GMV, *Galileo Reference Centre operations*, Noordwijk, Netherlands

---

*Author: Gamar Ismayilova | github.com/qama94*
