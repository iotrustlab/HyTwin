"""Portable CSV/JSON evidence and a dependency-free SVG research overview."""

import csv
import hashlib
import json
from html import escape
from pathlib import Path

from .experiments import Scenario, default_scenarios, simulate
from .model import Parameters, State


PROVENANCE = {
    "artifact_type": "illustrative reconstruction",
    "paper": "https://doi.org/10.1007/978-3-031-93706-4_17",
    "data_origin": "synthetic; chosen parameters; not recorded miniSWaT measurements",
    "integrator": "exact affine evolution per fixed scan; held constant flows",
    "physical_domain": "stop at an empty-tank boundary if further evolution would make a level negative",
    "units": "illustrative level units and seconds; rates are level units/second",
    "monitor": "hand-transcribed command compatibility predicates; not ModelPlex-generated",
    "detection": "attack-window-gated signature observation; no IDS performance claim",
    "mitigation": "trusted all-actuator freeze, latched every subsequent scan",
    "transfer_inflow": "demo keeps inflow open when permitted by a one-scan upper margin",
    "safety_interval": "closed; boundary contact is safe, a subsequent exceedance violates",
    "numerics": "Python float; safety comparisons use absolute tolerance 1e-10; residual alarm uses strict float comparison",
    "initialization": "nominal starts in paper A_tank; transfer scenarios start from a safe operating mode with v1 open",
    "violation_time": "infimum of unsafe times, analytically computed within affine segments",
    "proof_scope": "simulation is not a dL proof or a reproduction of the physical experiment",
}


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def overview_svg(results: list[dict], params: Parameters) -> str:
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="870" '
             'viewBox="0 0 1160 870" role="img" aria-labelledby="title desc">',
             '<title id="title">HyTwin: time to intervene</title>',
             '<desc id="desc">Synthetic constant-flow water-tank simulations. '
             'Timely intervention keeps levels safe; delayed intervention cannot undo a violation.</desc>',
             '<rect width="1160" height="870" fill="#0c1525"/>',
             '<g font-family="DejaVu Sans,Arial,sans-serif" fill="#e8eef8">',
             '<text x="48" y="52" font-size="16" fill="#61d5c4" letter-spacing="3">HYTWIN / RESEARCH ARTIFACT</text>',
             '<text x="48" y="96" font-size="32" font-weight="bold">How long can a defender wait?</text>',
             '<text x="48" y="125" font-size="15" fill="#b1c1d9">Formal safety analysis of industrial control systems under actuator attacks</text>',
             '<rect x="48" y="149" width="1064" height="34" rx="6" fill="#20304a"/>',
             '<text x="64" y="172" font-size="13">SYNTHETIC RECONSTRUCTION  /  chosen parameters  /  not the original miniSWaT traces</text>']
    groups = [
        ("Direct inflow attack", "Examples 2-5: attacker forces v1 = 1", "direct", "x1", 211),
        ("Transfer actuator attack", "Section 5: attacker forces p2 = v2 = 1", "transfer", "x2", 498),
    ]
    colors = {"unmitigated": "#ff7d86", "mitigated": "#61d5c4", "late": "#ffc369"}
    for title, subtitle, prefix, level, top in groups:
        left, plot_top, width, height = 94, top + 71, 990, 148
        candidates = [r for r in results if r["name"].startswith(prefix)]
        duration = max(r["settings"]["duration"] for r in candidates)
        ymax = max(params.upper + 2, max(r["max_" + level] for r in candidates) + 0.5)
        def px(t):
            return left + t / duration * width
        def py(x):
            return plot_top + height - x / ymax * height
        parts.extend([f'<text x="48" y="{top+21}" font-size="20" font-weight="bold">{title}</text>',
                      f'<text x="48" y="{top+45}" font-size="13" fill="#b1c1d9">{escape(subtitle)}</text>'])
        center_y = plot_top + height / 2
        parts.append(f'<text x="30" y="{center_y}" transform="rotate(-90,30,{center_y})" text-anchor="middle" font-size="11" fill="#b1c1d9">{level} (level units)</text>')
        for mark in (0, 4, 8, 12, 16, 20):
            if mark <= duration:
                x = px(mark)
                parts.append(f'<path d="M{x:.2f},{plot_top} v{height}" stroke="#25334a"/>')
                parts.append(f'<text x="{x:.2f}" y="{plot_top+height+20}" text-anchor="middle" font-size="11" fill="#b1c1d9">{mark}</text>')
        for value in (0, 4, 8, 12, 16):
            if value <= ymax:
                y = py(value)
                parts.append(f'<path d="M{left},{y:.2f} h{width}" stroke="#25334a"/>')
                parts.append(f'<text x="{left-12}" y="{y+4:.2f}" text-anchor="end" font-size="11" fill="#b1c1d9">{value}</text>')
        y = py(params.upper)
        parts.extend([f'<path d="M{left},{y:.2f} h{width}" stroke="#e8eef8" stroke-dasharray="5 5"/>',
                      f'<text x="{left+8}" y="{y-7:.2f}" font-size="11" fill="#e8eef8">HH = {params.upper:g}</text>'])
        onset = candidates[0]["attack_started_at_s"]
        deadline = onset + candidates[0]["held_command_horizon_at_attack_s"]
        for event_time, label in ((onset, "Attack starts"), (deadline, "Safety deadline")):
            x = px(event_time)
            parts.append(f'<path d="M{x:.2f},{plot_top} v{height}" stroke="#91a4c1" stroke-dasharray="2 6" opacity="0.55"/>')
            parts.append(f'<text x="{x+6:.2f}" y="{plot_top+13}" font-size="10" fill="#b1c1d9">{label}</text>')
        for r in candidates:
            key = r["name"].removeprefix(prefix + "-")
            color = colors[key]
            points = " ".join(f'{px(row["time_s"]):.2f},{py(row[level]):.2f}' for row in r["trace"])
            parts.append(f'<polyline points="{points}" stroke="{color}" fill="none" stroke-width="2.7"/>')
            if r["intervention_at_s"] is not None:
                x = px(r["intervention_at_s"])
                parts.append(f'<path d="M{x:.2f},{plot_top} v{height}" stroke="{color}" stroke-dasharray="3 5" opacity="0.7"/>')
        for i, r in enumerate(candidates):
            key = r["name"].removeprefix(prefix + "-")
            label = {"unmitigated": "No intervention", "mitigated": "Timely intervention", "late": "Late intervention"}[key]
            x = 120 + i * 320
            y = plot_top + height + 47
            parts.append(f'<path d="M{x},{y-5} h22" stroke="{colors[key]}" stroke-width="3"/>')
            parts.append(f'<text x="{x+30}" y="{y}" font-size="12" fill="{colors[key]}">{label}</text>')
        parts.append(f'<text x="{left+width}" y="{plot_top+height+20}" text-anchor="end" font-size="11" fill="#b1c1d9" dy="16">Time (s)</text>')
    parts.extend(['<text x="48" y="824" font-size="14" font-weight="bold">The deadline comes from physics:  horizon = remaining safety margin / adverse net rate</text>',
                  '<text x="48" y="849" font-size="12" fill="#b1c1d9">Run: python3 -m hytwin demo --output results/demo   |   Paper: NFM 2025, DOI 10.1007/978-3-031-93706-4_17</text>',
                  '</g></svg>'])
    return "\n".join(parts) + "\n"


def delay_sweep(params: Parameters) -> list[dict]:
    rows = []
    for tick in range(81):
        delay = tick * 0.25
        result = simulate(Scenario("transfer-sweep", "transfer", response_delay=delay,
                                   duration=24.0, initial=State(7.0, 6.0, 1)), params)
        rows.append({"requested_delay_s": delay,
                     "actual_response_delay_s": result["actual_response_delay_s"],
                     "held_command_horizon_s": result["held_command_horizon_at_attack_s"],
                     "safe_entire_run": result["safe_entire_run"],
                     "max_x2": result["max_x2"],
                     "violation_boundary_time_s": result["violation_boundary_time_s"]})
    return rows


def write_csv(path: Path, rows: list[dict]):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate_demo(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    params = Parameters()
    results = [simulate(s, params) for s in default_scenarios()]
    summary = {"schema_version": 1, "provenance": PROVENANCE,
               "parameters": params.__dict__,
               "scenarios": [{k: v for k, v in r.items() if k != "trace"} for r in results]}
    write_json(output / "summary.json", summary)
    write_csv(output / "traces.csv", [row for r in results for row in r["trace"]])
    write_csv(output / "delay-sweep.csv", delay_sweep(params))
    (output / "overview.svg").write_text(overview_svg(results, params), encoding="utf-8")
    manifest = {"schema_version": 1, "provenance": PROVENANCE,
                "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(output.iterdir()) if p.name in
                          ("summary.json", "traces.csv", "delay-sweep.csv", "overview.svg")}}
    write_json(output / "manifest.json", manifest)
    return summary
