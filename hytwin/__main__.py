"""Run with python3 -m hytwin; the default demo requires only the standard library."""

import argparse
from dataclasses import asdict
from pathlib import Path

from .experiments import Scenario, simulate
from .model import Parameters, State
from .report import PROVENANCE, generate_demo, write_csv, write_json


def main():
    parser = argparse.ArgumentParser(description="HyTwin: illustrative reconstruction of timed ICS safety interventions")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Generate six scenarios, a delay sweep, CSV/JSON and an SVG overview")
    demo.add_argument("--output", type=Path, default=Path("results/demo"))
    run = commands.add_parser("run", help="Explore a synthetic constant-flow actuator attack")
    run.add_argument("--attack", choices=("direct", "transfer"), default="transfer")
    run.add_argument("--delay", type=float, default=2.0, help="Seconds from signature observation; defaults to 2")
    run.add_argument("--unmitigated", action="store_true")
    run.add_argument("--scan", type=float, default=0.25)
    run.add_argument("--inflow", type=float, default=0.5)
    run.add_argument("--transfer", type=float, default=0.4)
    run.add_argument("--duration", type=float, default=24.0)
    run.add_argument("--output", type=Path, default=Path("results/local"))
    args = parser.parse_args()
    try:
        if args.command == "demo":
            summary = generate_demo(args.output)
            for r in summary["scenarios"]:
                status = "SAFE" if r["safe_entire_run"] else "VIOLATION"
                print(f'{r["name"]:24} {status:10} max x1={r["max_x1"]:.2f}  max x2={r["max_x2"]:.2f}')
        else:
            params = Parameters(scan=args.scan, inflow=args.inflow, transfer=args.transfer)
            initial = State(7.0, 6.0, 1) if args.attack == "transfer" else State(6.0, 6.0)
            scenario = Scenario("custom", args.attack, response_delay=None if args.unmitigated else args.delay,
                                duration=args.duration, initial=initial)
            result = simulate(scenario, params)
            args.output.mkdir(parents=True, exist_ok=True)
            write_csv(args.output / "traces.csv", result.pop("trace"))
            write_json(args.output / "summary.json", {"provenance": PROVENANCE, "parameters": asdict(params), **result})
            print("SAFE" if result["safe_entire_run"] else "VIOLATION")
            print(f'Held-command horizon at attack: {result["held_command_horizon_at_attack_s"]} s')
            print(f'Actual intervention delay: {result["actual_response_delay_s"]} s')
        print(f"Artifacts: {args.output.resolve()}")
        print("Synthetic reconstruction; not original miniSWaT measurements or a formal proof.")
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
