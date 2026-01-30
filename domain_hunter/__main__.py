import argparse
import sys

from domain_hunter.app import run
from domain_hunter.config import load_config


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bitcointalk domain hunter")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML config")
    parser.add_argument("--once", action="store_true", help="Run a single cycle")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    config = load_config(args.config)
    run(config, run_once=args.once)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
