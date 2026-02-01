"""Generate a JSON template for match extraction/insertion.

Usage:
  python scripts/generate_match_template.py --match-date 20260118 --match-session 03 --team yb --players 30
"""

import argparse
import json
from pathlib import Path

TEMPLATE_PLAYER = {
    "player_name": "",
    "defeated": 0,
    "assist": 0,
    "defeated_2": 0,
    "fun_coin": 0,
    "damage": 0,
    "tank": 0,
    "heal": 0,
    "siege_damage": 0,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate match JSON template")
    parser.add_argument("--match-date", required=True, help="YYYYMMDD")
    parser.add_argument("--match-session", required=True, help="Match session (01, 02, 03)")
    parser.add_argument("--team", required=True, choices=["yb", "enemy"], help="Team")
    parser.add_argument("--players", type=int, default=30, help="Number of player rows")
    parser.add_argument("--out", default=None, help="Output JSON path")

    args = parser.parse_args()

    payload = {
        "match_date": args.match_date,
        "match_session": str(args.match_session).zfill(2),
        "team": "YoungBuffalo" if args.team == "yb" else "Enemy",
        "players": [TEMPLATE_PLAYER.copy() for _ in range(args.players)],
    }

    out_path = (
        Path(args.out)
        if args.out
        else Path("outputs") / "templates" / f"{args.match_date}_{payload['match_session']}_{args.team}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Template written to: {out_path}")


if __name__ == "__main__":
    main()
