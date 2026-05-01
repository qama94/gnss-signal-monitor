"""
Galileo / GPS Signal Quality Monitor
=====================================
Main entry point.

Usage:
    # Synthetic data (demo):
    python main.py

    # Real RINEX file:
    python main.py --rinex path/to/WSRT00NLD_R_20261150000_01D_30S_MO.rnx

    # Download IGS sample and run:
    python main.py --download --station WSRT --year 2026 --doy 115
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_generator   import generate
from signal_monitor   import run_monitoring
from visualiser       import plot_dashboard
from report_generator import generate_text_report


def main():
    parser = argparse.ArgumentParser(description='GNSS Signal Quality Monitor')
    parser.add_argument('--rinex',    type=str,  help='Path to RINEX 3 obs file')
    parser.add_argument('--download', action='store_true',
                        help='Download IGS sample RINEX file')
    parser.add_argument('--station',  type=str,  default='WSRT')
    parser.add_argument('--year',     type=int,  default=2026)
    parser.add_argument('--doy',      type=int,  default=115)
    parser.add_argument('--hours',    type=float, default=6,
                        help='Duration for synthetic data (hours)')
    parser.add_argument('--output',   type=str,  default='results')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # ── Load data ──────────────────────────────────────────────────────────
    if args.download:
        from rinex_parser import download_igs_sample, parse_rinex_obs
        rinex_path = download_igs_sample(args.station, args.year,
                                         args.doy, args.output)
        df = parse_rinex_obs(rinex_path)

    elif args.rinex:
        from rinex_parser import parse_rinex_obs
        print(f"Parsing RINEX file: {args.rinex}")
        df = parse_rinex_obs(args.rinex)

    else:
        print("No RINEX file provided — using realistic synthetic data.")
        print("To use real data: python main.py --rinex your_file.rnx\n")
        df = generate(duration_hours=args.hours, inject_events=True)

    print(f"Loaded {len(df)} observations | "
          f"{df['sv'].nunique()} SVs | "
          f"{df['epoch'].nunique()} epochs\n")

    # ── Run monitoring ─────────────────────────────────────────────────────
    result = run_monitoring(df)

    # ── Outputs ────────────────────────────────────────────────────────────
    plot_dashboard(df, result, output_dir=args.output)
    generate_text_report(df, result, output_dir=args.output)


if __name__ == '__main__':
    main()
