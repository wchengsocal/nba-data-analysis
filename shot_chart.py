"""
Shot chart analysis — hexbin aggregation, zone efficiency, hot/cold zones.
"""
import numpy as np
import pandas as pd
from typing import Any


ZONE_DEFINITIONS = {
    "Restricted Area": {"x_range": (-80, 80), "y_range": (-50, 40), "is_3": False},
    "In The Paint (Non-RA)": {"x_range": (-150, 150), "y_range": (-50, 140), "is_3": False},
    "Mid-Range": {"x_range": (-250, 250), "y_range": (-50, 420), "is_3": False},
    "Left Corner 3": {"x_range": (-250, -220), "y_range": (-50, 90), "is_3": True},
    "Right Corner 3": {"x_range": (220, 250), "y_range": (-50, 90), "is_3": True},
    "Above the Break 3": {"x_range": (-250, 250), "y_range": (90, 420), "is_3": True},
}

LEAGUE_AVG_FG_PCT = {
    "Restricted Area": 0.641,
    "In The Paint (Non-RA)": 0.398,
    "Mid-Range": 0.413,
    "Left Corner 3": 0.384,
    "Right Corner 3": 0.387,
    "Above the Break 3": 0.358,
}


def compute_zone_efficiency(shots: list[dict]) -> list[dict]:
    """
    Aggregate shots by zone and compute FG%, points per shot (PPS),
    and delta vs league average.
    """
    df = pd.DataFrame(shots)
    if df.empty:
        return []

    zone_col = "SHOT_ZONE_BASIC"
    made_col = "SHOT_MADE_FLAG"

    results = []
    for zone, group in df.groupby(zone_col):
        attempts = len(group)
        makes = group[made_col].sum()
        fg_pct = makes / attempts if attempts > 0 else 0
        is_3 = "3" in str(group["SHOT_TYPE"].iloc[0]) if "SHOT_TYPE" in group.columns else False
        pts_value = 3 if is_3 else 2
        pps = fg_pct * pts_value
        league_avg = LEAGUE_AVG_FG_PCT.get(zone, fg_pct)
        delta = fg_pct - league_avg

        results.append({
            "zone": zone,
            "attempts": int(attempts),
            "makes": int(makes),
            "fg_pct": round(fg_pct, 3),
            "pps": round(pps, 3),
            "league_avg_fg_pct": league_avg,
            "delta_vs_avg": round(delta, 3),
            "efficiency_label": _label(delta),
        })

    return sorted(results, key=lambda x: x["attempts"], reverse=True)


def compute_hexbins(shots: list[dict], gridsize: int = 25) -> list[dict]:
    """
    Compute hexbin grid for the shot chart heatmap.
    Returns list of {x, y, count, fg_pct} for each non-empty hex cell.
    """
    df = pd.DataFrame(shots)
    if df.empty:
        return []

    x = df["LOC_X"].values
    y = df["LOC_Y"].values
    made = df["SHOT_MADE_FLAG"].values

    # Build grid
    x_bins = np.linspace(-250, 250, gridsize + 1)
    y_bins = np.linspace(-50, 420, gridsize + 1)

    hexbins = []
    for i in range(len(x_bins) - 1):
        for j in range(len(y_bins) - 1):
            mask = (
                (x >= x_bins[i]) & (x < x_bins[i + 1]) &
                (y >= y_bins[j]) & (y < y_bins[j + 1])
            )
            count = mask.sum()
            if count >= 2:
                fg = made[mask].mean()
                hexbins.append({
                    "x": round(float((x_bins[i] + x_bins[i + 1]) / 2), 1),
                    "y": round(float((y_bins[j] + y_bins[j + 1]) / 2), 1),
                    "count": int(count),
                    "fg_pct": round(float(fg), 3),
                })

    return hexbins


def _label(delta: float) -> str:
    if delta > 0.05:
        return "hot"
    elif delta < -0.05:
        return "cold"
    return "average"
