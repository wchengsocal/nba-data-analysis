"""
Player comparison — percentile ranks, radar chart data, head-to-head career overlays.
"""
import numpy as np
import pandas as pd


RADAR_STATS = ["PTS_PER_G", "REB_PER_G", "AST_PER_G", "STL", "BLK", "FG_PCT", "FG3_PCT"]
RADAR_LABELS = ["Points", "Rebounds", "Assists", "Steals", "Blocks", "FG%", "3P%"]

# Approximate league-average ranges for percentile scaling (per-game, regular season)
STAT_RANGES = {
    "PTS_PER_G": (0, 36),
    "REB_PER_G": (0, 18),
    "AST_PER_G": (0, 12),
    "STL":       (0, 3.5),
    "BLK":       (0, 3.5),
    "FG_PCT":    (0.3, 0.72),
    "FG3_PCT":   (0.25, 0.55),
}


def build_radar(player1_stats: list[dict], player2_stats: list[dict]) -> dict:
    """
    Return radar chart data for the most recent season of each player.
    Values are normalised 0–100 within known stat ranges.
    """
    p1 = _latest_season(player1_stats)
    p2 = _latest_season(player2_stats)

    p1_vals = _normalise(p1)
    p2_vals = _normalise(p2)

    return {
        "labels": RADAR_LABELS,
        "player1": p1_vals,
        "player2": p2_vals,
        "player1_raw": {k: p1.get(k, 0) for k in RADAR_STATS},
        "player2_raw": {k: p2.get(k, 0) for k in RADAR_STATS},
    }


def build_career_overlay(player1_stats: list[dict], player2_stats: list[dict], stat: str = "PTS_PER_G") -> dict:
    """
    Align two career timelines by year-in-league (season 1, season 2, …)
    so players from different eras can be compared fairly.
    """
    def extract(stats, label):
        return [
            {"year": i + 1, "value": round(float(s.get(stat, 0)), 1), "player": label, "season": s.get("SEASON_ID", "")}
            for i, s in enumerate(stats)
        ]

    return {
        "stat": stat,
        "player1": extract(player1_stats, "player1"),
        "player2": extract(player2_stats, "player2"),
    }


def build_season_table(player1_stats: list[dict], player2_stats: list[dict]) -> dict:
    """Return best single-season and career average rows for both players."""
    def best_season(stats):
        if not stats:
            return {}
        return max(stats, key=lambda s: float(s.get("PTS_PER_G", 0)))

    def career_avg(stats):
        if not stats:
            return {}
        df = pd.DataFrame(stats)
        numeric = df.select_dtypes(include="number")
        return numeric.mean().round(2).to_dict()

    return {
        "player1": {"best": best_season(player1_stats), "avg": career_avg(player1_stats)},
        "player2": {"best": best_season(player2_stats), "avg": career_avg(player2_stats)},
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _latest_season(stats: list[dict]) -> dict:
    if not stats:
        return {}
    return stats[-1]


def _normalise(row: dict) -> list[float]:
    vals = []
    for stat in RADAR_STATS:
        lo, hi = STAT_RANGES[stat]
        raw = float(row.get(stat) or 0)
        norm = max(0.0, min(100.0, (raw - lo) / (hi - lo) * 100))
        vals.append(round(norm, 1))
    return vals
