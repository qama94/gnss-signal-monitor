# Galileo / GPS Signal Quality Monitor

A Python tool for monitoring GNSS signal quality and service performance,
built around the operational methodology of the Galileo Reference Centre (GRC)
in Noordwijk, Netherlands.

---

## What it does

- **Service availability** - % of epochs with >= 4 valid satellites per constellation
- **C/N0 statistics** - Mean, std, 5th percentile by constellation and elevation band
- **Anomaly detection** - Low signal events below 32 dB-Hz, classified by severity
- **Signal continuity** - Tracking gap detection
- **Multi-system comparison** - Galileo vs GPS C/N0 performance delta

Outputs: 4-panel monitoring dashboard and structured GRC-style performance report

---

## Quick start

    git clone https://github.com/qama94/gnss-signal-monitor.git
    cd gnss-signal-monitor
    pip install numpy pandas matplotlib
    python main.py

Check the results/ folder for:
- monitoring_dashboard.png - open this to see the plots
- monitoring_report.txt - structured performance report

---

## Project structure

    gnss-signal-monitor/
    main.py
    src/
        signal_monitor.py      - core metrics and anomaly detection
        data_generator.py      - realistic synthetic data (Galileo E1 OS)
        visualiser.py          - 4-panel monitoring dashboard
        report_generator.py    - structured monitoring report
    results/
    data/

---

## Using real GNSS data

Real RINEX 3 observation files are freely available from the IGS network.

Recommended European stations (include Galileo observations):
- WSRT - Westerbork, Netherlands
- BRUX - Brussels, Belgium
- WARN - Warnemunde, Germany

    pip install georinex
    python main.py --rinex your_file.rnx

---

## Signal quality model

C/N0 modelled as a function of elevation angle, calibrated against
EUSPA Galileo Open Service Performance Assessment data:

    C/N0(elev) = C/N0_zenith + k * elev + noise

Where:
- C/N0_zenith = 44.5 dB-Hz (Galileo E1 OS), 42.5 dB-Hz (GPS L1 C/A)
- k = 0.32 dB-Hz per degree elevation
- noise ~ N(0, 1.8) dB-Hz

---

## Roadmap

- Real RINEX file parsing via georinex
- Grafana-compatible JSON metrics export
- Alert system for threshold violations
- Multi-station network monitoring
- GLONASS and BeiDou support

---

## References

- EUSPA, Galileo Open Service Performance Assessment, 2024
- IGS, RINEX 3 Observation Data Format, v3.05
- GMV, Galileo Reference Centre operations, Noordwijk, Netherlands

---

Author: Gamar Ismayilova | github.com/qama94
