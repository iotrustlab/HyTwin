"""Piecewise constant-flow tank model, in level units per second.

This is a new executable specialization, not the original miniSWaT plant.
The controller follows paper Example 1; sampled constant flows and a fixed scan
duration choose one behavior from the paper's nondeterministic hybrid program.
"""

from dataclasses import dataclass, replace
from math import inf, isfinite


@dataclass(frozen=True)
class Parameters:
    lower: float = 1.0
    upper: float = 12.0
    low1: float = 4.0
    high1: float = 7.0
    low2: float = 4.0
    high2: float = 7.0
    inflow: float = 0.5
    transfer: float = 0.4
    scan: float = 0.25

    def __post_init__(self):
        if not all(isfinite(v) for v in self.__dict__.values()):
            raise ValueError("All plant parameters must be finite")
        if not (0 <= self.lower < self.low1 < self.high1 < self.upper
                and self.lower < self.low2 < self.high2 < self.upper):
            raise ValueError("Require 0 <= lower < low < high < upper for each tank")
        if self.scan <= 0 or min(self.inflow, self.transfer) < 0:
            raise ValueError("Scan must be positive and flows nonnegative")


@dataclass(frozen=True)
class State:
    x1: float
    x2: float
    v1: int = 0
    v2: int = 0
    p2: int = 0

    def __post_init__(self):
        if not all(isfinite(x) for x in (self.x1, self.x2)):
            raise ValueError("Levels must be finite")
        if any(x not in (0, 1) for x in (self.v1, self.v2, self.p2)):
            raise ValueError("Actuator values must be binary")


def rates(state: State, params: Parameters) -> tuple[float, float]:
    q12 = state.v2 * state.p2 * params.transfer
    return state.v1 * params.inflow - q12, q12


def control(state: State, params: Parameters) -> State:
    """Example 1 inflow; outflow; protect, using truthful level readings.

    high1/high2 define startup bounds, not switching guards: the paper uses
    the one-scan safety margin to HH and the low thresholds for latching.
    """
    v1, v2, p2 = state.v1, state.v2, state.p2
    if params.inflow > (params.upper - state.x1) / params.scan:
        v1 = 0
    elif state.x1 <= params.low1:
        v1 = 1
    if state.x2 <= params.low2:
        p2, v2 = 1, 1
    q12 = v2 * p2 * params.transfer
    if (v1 * params.inflow - q12 < (params.lower - state.x1) / params.scan
            or q12 > (params.upper - state.x2) / params.scan):
        p2, v2 = 0, 0
    return replace(state, v1=v1, v2=v2, p2=p2)


def evolve(state: State, params: Parameters, duration: float) -> State:
    """Exact affine evolution; never clip levels to the safety interval."""
    if not isfinite(duration) or duration < 0:
        raise ValueError("Duration must be finite and nonnegative")
    d1, d2 = rates(state, params)
    return replace(state, x1=state.x1 + d1 * duration,
                   x2=state.x2 + d2 * duration)


def safe(state: State, params: Parameters, tolerance: float = 1e-10) -> bool:
    return all(params.lower - tolerance <= x <= params.upper + tolerance
               for x in (state.x1, state.x2))


def safety_horizon(state: State, params: Parameters) -> float:
    """Time to the first closed safety boundary under held current commands.

    Infinity means no boundary is approached. Zero also denotes an already
    unsafe state, so callers must separately check safe(). This fixed-rate
    witness is not a universal horizon for arbitrary future controller choices.
    """
    if not safe(state, params):
        return 0.0
    candidates = []
    for level, rate in zip((state.x1, state.x2), rates(state, params)):
        if rate > 0:
            candidates.append(max(0.0, (params.upper - level) / rate))
        elif rate < 0:
            candidates.append(max(0.0, (level - params.lower) / -rate))
    return min(candidates, default=inf)


def direct_signature(state: State) -> bool:
    """Example 4: compatibility with v1 := 1; benign commands can match."""
    return state.v1 == 1


def transfer_signature(state: State) -> bool:
    """Section 5 command pattern; this predicate alone cannot attribute attack."""
    return state.v2 == 1 and state.p2 == 1


def residual_alarm(measured: float, predicted: float, delta: float) -> bool:
    """Section 4 strict detector evaluated with Python floating-point arithmetic.

    Decimal equality can round across the threshold; this is not an exact-real
    monitor implementation. Use representable boundaries when illustrating
    equality, and account for numerical/sensor error in a deployed monitor.
    """
    if not all(isfinite(x) for x in (measured, predicted, delta)) or delta < 0:
        raise ValueError("Residual inputs must be finite; delta must be nonnegative")
    return abs(measured - predicted) > delta
