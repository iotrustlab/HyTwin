"""Deterministic illustrative scenarios with explicit provenance and event times."""

from dataclasses import asdict, dataclass, replace
from math import ceil, isfinite

from .model import (Parameters, State, control, direct_signature, evolve,
                    rates, safe, safety_horizon, transfer_signature)


@dataclass(frozen=True)
class Scenario:
    name: str
    attack: str = "none"
    attack_at: float = 2.0
    response_delay: float | None = None
    duration: float = 20.0
    initial: State = State(6.0, 6.0)

    def __post_init__(self):
        if self.attack not in ("none", "direct", "transfer"):
            raise ValueError("Unknown attack")
        if (not isfinite(self.duration) or self.duration <= 0
                or not isfinite(self.attack_at) or self.attack_at < 0):
            raise ValueError("Duration must be positive; attack time nonnegative")
        if self.response_delay is not None and (
                not isfinite(self.response_delay) or self.response_delay < 0):
            raise ValueError("Response delay must be finite and nonnegative")


def default_scenarios() -> list[Scenario]:
    return [
        Scenario("nominal", initial=State(4.0, 4.0)),
        Scenario("direct-unmitigated", "direct"),
        Scenario("direct-mitigated", "direct", response_delay=2.0),
        Scenario("transfer-unmitigated", "transfer", initial=State(7.0, 6.0, 1)),
        Scenario("transfer-mitigated", "transfer", response_delay=2.0,
                 initial=State(7.0, 6.0, 1)),
        Scenario("transfer-late", "transfer", response_delay=16.0,
                 initial=State(7.0, 6.0, 1)),
    ]


def simulate(scenario: Scenario, params: Parameters = Parameters()) -> dict:
    """Sense/control, attack overwrite, trusted mitigation, affine physics.

    Attacks persist after onset. A latched trusted intervention overwrites each
    subsequent scan, freezing both tanks. Responses occur on the first scan at
    or after the sampled signature observation plus response_delay; scan
    alignment is included in metrics.
    Both transfer cases use a low-threshold, upper-margin inflow controller
    override to keep tank 1 supplied while filling tank 2. It is labeled in the
    manifest and is not the paper's original testbed logic.
    """
    if not safe(scenario.initial, params):
        raise ValueError("Scenario must start inside the safety interval")
    scan_count = scenario.duration / params.scan
    if not isfinite(scan_count) or scan_count > 1_000_000:
        raise ValueError("Scenario exceeds one million scans")
    step_count = ceil(scan_count)
    state = scenario.initial
    rows = []
    detected_at = intervention_at = attack_started_at = None
    horizon_at_attack = None
    first_violation = None
    physical_domain_exit = None
    min_x1 = max_x1 = state.x1
    min_x2 = max_x2 = state.x2
    active = latched = False

    def record(time, event):
        rows.append({"scenario": scenario.name, "time_s": round(time, 10),
                     **asdict(state), "attack_active": active,
                     "mitigation_active": latched, "event": event,
                     "safe": safe(state, params)})

    record(0.0, "initial")
    for tick in range(step_count):
        time = tick * params.scan
        dt = min(params.scan, scenario.duration - time)
        state = control(state, params)
        active = scenario.attack != "none" and time + 1e-12 >= scenario.attack_at
        event = "scan"
        if active:
            if scenario.attack == "direct":
                state = replace(state, v1=1)
                signature = direct_signature(state)
            else:
                # An explicit demo choice: keep tank 1 supplied if safe for this scan.
                v1 = int(params.inflow <= (params.upper - state.x1) / params.scan)
                state = replace(state, v1=v1, v2=1, p2=1)
                signature = transfer_signature(state)
            if attack_started_at is None:
                attack_started_at = time
                horizon_at_attack = safety_horizon(state, params)
                event = "attack-start"
            if signature and detected_at is None:
                # Oracle eligibility: demo knows the attack window. Not an IDS metric.
                detected_at = time
            if (scenario.response_delay is not None and detected_at is not None
                    and time + 1e-12 >= detected_at + scenario.response_delay):
                latched = True
                if intervention_at is None:
                    intervention_at = time
                    event = "intervention"
        if latched:
            state = replace(state, v1=0, v2=0, p2=0)
        record(time, event)
        # Exact boundary crossing time for affine trajectories; HH and LL are safe.
        d1, d2 = rates(state, params)
        # Match Q_tank: a trajectory cannot evolve past an empty tank. Stop the
        # run at that physical boundary, while retaining any prior LL violation.
        domain_limited = False
        for level, rate in zip((state.x1, state.x2), (d1, d2)):
            if rate < 0 and level + rate * dt < 0:
                dt = max(0.0, level / -rate)
                domain_limited = True
        crossings = []
        for level, rate in zip((state.x1, state.x2), (d1, d2)):
            if rate > 0 and level + rate * dt > params.upper + 1e-10:
                crossings.append(time + max(0.0, (params.upper - level) / rate))
            elif rate < 0 and level + rate * dt < params.lower - 1e-10:
                crossings.append(time + max(0.0, (level - params.lower) / -rate))
        if first_violation is None and crossings:
            first_violation = min(crossings)
        state = evolve(state, params, dt)
        min_x1, max_x1 = min(min_x1, state.x1), max(max_x1, state.x1)
        min_x2, max_x2 = min(min_x2, state.x2), max(max_x2, state.x2)
        record(time + dt, "plant-end")
        if domain_limited:
            physical_domain_exit = time + dt
            rows[-1]["event"] = "physical-domain-stop"
            break

    # Never serialize Infinity: null is accompanied by explicit horizon status.
    finite_horizon = horizon_at_attack is not None and isfinite(horizon_at_attack)
    return {
        "name": scenario.name,
        "settings": {**asdict(scenario), "initial": asdict(scenario.initial)},
        "paper_reference": ("Example 1" if scenario.attack == "none" else
                            "Examples 2-5" if scenario.attack == "direct" else
                            "Section 5, Figures 2-3 (qualitative only)"),
        "attack_started_at_s": attack_started_at,
        "signature_observed_at_s": detected_at,
        "intervention_at_s": intervention_at,
        "actual_response_delay_s": (None if intervention_at is None else
                                     intervention_at - detected_at),
        "held_command_horizon_at_attack_s": horizon_at_attack if finite_horizon else None,
        "held_command_horizon_status": ("finite" if finite_horizon else
                                         "not-applicable" if horizon_at_attack is None else "unbounded"),
        "safe_entire_run": first_violation is None,
        "violation_boundary_time_s": first_violation,
        "completed_duration_s": rows[-1]["time_s"],
        "termination": "physical-domain-boundary" if physical_domain_exit is not None else "duration-complete",
        "min_x1": min_x1, "max_x1": max_x1,
        "min_x2": min_x2, "max_x2": max_x2,
        "final_state": asdict(state),
        "trace": rows,
    }
