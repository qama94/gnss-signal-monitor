"""
RINEX 3 Observation File Parser
================================
Parses RINEX 3.x observation files to extract C/N0 observations
for Galileo (E) and GPS (G) constellations.

Requirements:
    pip install georinex

Public IGS data sources:
    - BKG:   https://igs.bkg.bund.de/root_ftp/IGS/obs/YYYY/DDD/
    - CDDIS: https://cddis.nasa.gov/archive/gnss/data/daily/YYYY/DDD/
    - IGN:   https://igs.ign.fr/pub/igs/data/YYYY/DDD/

Recommended stations (Europe, include Galileo):
    BRUX (Brussels), WARN (Warnemunde), WSRT (Westerbork, NL),
    ONSA (Onsala), ZIMM (Zimmerwald)

File format note:
    IGS distributes Hatanaka-compressed files (.crx).
    Decompress with: crx2rnx file.crx or use hatanaka Python package.

Example usage:
    from src.rinex_parser import parse_rinex_obs
    df = parse_rinex_obs('WSRT00NLD_R_20261150000_01D_30S_MO.rnx')
"""

import numpy as np
import pandas as pd
from pathlib import Path

try:
    import georinex as gr
    GEORINEX_AVAILABLE = True
except ImportError:
    GEORINEX_AVAILABLE = False


def parse_rinex_obs(filepath: str,
                    constellations: list = ['E', 'G']) -> pd.DataFrame:
    """
    Parse RINEX 3 observation file.

    Parameters
    ----------
    filepath : str
        Path to uncompressed RINEX 3 observation file (.rnx or .obs)
    constellations : list
        Constellation prefixes: 'E' = Galileo, 'G' = GPS

    Returns
    -------
    pd.DataFrame: epoch, sv, constellation, cn0, valid
    Note: elevation not available from obs file alone (needs nav + position).
    """
    if not GEORINEX_AVAILABLE:
        raise ImportError(
            "Install georinex: pip install georinex\n"
            "Download RINEX data from IGS: "
            "https://igs.bkg.bund.de/root_ftp/IGS/obs/"
        )

    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"RINEX file not found: {filepath}")

    obs = gr.load(str(path), use=' '.join(constellations))
    signal_obs = [v for v in obs.data_vars if v.startswith('S')]

    records = []
    for sv in obs.sv.values:
        if sv[0] not in constellations:
            continue
        constellation = 'Galileo' if sv[0] == 'E' else 'GPS'

        for t in obs.time.values:
            cn0 = None
            for s_obs in signal_obs:
                val = float(obs[s_obs].sel(sv=sv, time=t).values)
                if not np.isnan(val) and val > 0:
                    cn0 = round(val, 2)
                    break

            if cn0 is not None:
                records.append({
                    'epoch': pd.Timestamp(t).to_pydatetime(),
                    'sv': sv,
                    'constellation': constellation,
                    'cn0': cn0,
                    'elevation': None,
                    'valid': cn0 >= 30.0
                })

    df = pd.DataFrame(records)
    print(f"Parsed {len(df)} observations | "
          f"{df['sv'].nunique()} SVs | "
          f"{df['epoch'].nunique()} epochs")
    return df
