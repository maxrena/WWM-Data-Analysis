"""Match data ingestion helpers for consistent schema and IDs."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Iterable, List

import pandas as pd

REQUIRED_COLUMNS: List[str] = [
    "player_name",
    "defeated",
    "assist",
    "defeated_2",
    "fun_coin",
    "damage",
    "tank",
    "heal",
    "siege_damage",
]


@dataclass(frozen=True)
class MatchId:
    match_date: str  # YYYYMMDD
    match_session: str  # 2-digit session

    def value(self) -> str:
        return f"{self.match_date}_{self.match_session}"


def normalize_match_id(match_date: str, match_session: int | str) -> MatchId:
    """Normalize match date/session into a stable match id."""
    session_str = str(match_session).zfill(2)
    return MatchId(match_date=match_date, match_session=session_str)


def validate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure dataframe has required columns in correct order."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    return df[REQUIRED_COLUMNS].copy()


def _session_table_name(team: str, match_id: str) -> str:
    if team.lower() == "yb":
        return f"yb_stats_{match_id}"
    return f"enemy_stats_{match_id}"


def _aggregate_table_name(team: str) -> str:
    if team.lower() == "yb":
        return "youngbuffalo_stats"
    return "enemy_all_stats"


def insert_team_stats(
    conn: sqlite3.Connection,
    team: str,
    match_id: MatchId,
    df: pd.DataFrame,
) -> None:
    """Insert team stats into session + aggregate tables with consistent schema."""
    cleaned = validate_columns(df)

    session_df = cleaned.copy()
    session_df["match_date"] = match_id.match_date
    session_df["match_session"] = match_id.match_session
    session_df["team"] = "YoungBuffalo" if team.lower() == "yb" else "Enemy"

    session_table = _session_table_name(team, match_id.value())
    session_df.to_sql(session_table, conn, if_exists="replace", index=False)

    aggregate_df = cleaned.copy()
    aggregate_df["match_date"] = match_id.match_date
    aggregate_df["match_id"] = match_id.value()

    aggregate_table = _aggregate_table_name(team)
    cursor = conn.cursor()
    cursor.execute(
        f"DELETE FROM {aggregate_table} WHERE match_id = ?",
        (match_id.value(),),
    )
    conn.commit()

    aggregate_df.to_sql(aggregate_table, conn, if_exists="append", index=False)
