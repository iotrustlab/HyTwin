import math
import random
import unittest
from dataclasses import replace

from hytwin.experiments import Scenario, default_scenarios, simulate
from hytwin.model import (Parameters, State, control, direct_signature, evolve,
                          rates, residual_alarm, safe, safety_horizon)


class PhysicalModelTests(unittest.TestCase):
    def test_transfer_conserves_total_water_without_inflow(self):
        params = Parameters()
        initial = State(7, 3, v2=1, p2=1)
        after = evolve(initial, params, 4)
        self.assertAlmostEqual(initial.x1 + initial.x2, after.x1 + after.x2)
        self.assertLess(after.x1, initial.x1)
        self.assertGreater(after.x2, initial.x2)

    def test_upper_horizon_includes_boundary_but_not_later_times(self):
        params = Parameters()
        state = State(6, 6, v1=1)
        tau = safety_horizon(state, params)
        self.assertEqual(tau, 12)
        self.assertTrue(safe(evolve(state, params, tau), params))
        self.assertFalse(safe(evolve(state, params, tau + 0.001), params))

    def test_lower_horizon_accounts_for_drain_before_other_tank_overflows(self):
        params = Parameters()
        state = State(2, 3, v2=1, p2=1)
        self.assertEqual(safety_horizon(state, params), 2.5)
        self.assertTrue(safe(evolve(state, params, 2.5), params))
        self.assertFalse(safe(evolve(state, params, 2.6), params))

    def test_zero_flow_and_outside_interval(self):
        params = Parameters()
        self.assertEqual(safety_horizon(State(6, 6), params), math.inf)
        self.assertEqual(safety_horizon(State(13, 6), params), 0)
        self.assertFalse(safe(State(13, 6), params))

    def test_true_levels_do_not_change_when_attack_changes_commands(self):
        state = State(6, 6)
        attacked = replace(state, v1=1)
        self.assertEqual((attacked.x1, attacked.x2), (state.x1, state.x2))
        self.assertNotEqual(rates(state, Parameters()), rates(attacked, Parameters()))

    def test_signature_compatibility_does_not_imply_malice(self):
        benign = control(State(3, 6), Parameters())
        self.assertTrue(direct_signature(benign))

    def test_sensor_attack_at_residual_boundary_is_stealthy(self):
        self.assertFalse(residual_alarm(measured=7.5, predicted=8, delta=0.5))
        self.assertTrue(residual_alarm(measured=7.4, predicted=8, delta=0.5))

    def test_controller_preserves_one_scan_safety_for_varied_safe_states(self):
        # Samples challenge protection guards and actuator latch memory.
        # This regression check is not a universal invariant proof.
        rng = random.Random(2025)
        for _ in range(500):
            params = Parameters(inflow=rng.uniform(0, 3), transfer=rng.uniform(0, 3),
                                scan=rng.uniform(0.01, 2))
            state = State(rng.uniform(1, 12), rng.uniform(1, 12),
                          rng.randrange(2), rng.randrange(2), rng.randrange(2))
            self.assertTrue(safe(evolve(control(state, params), params, params.scan), params))

    def test_invalid_parameters_fail_explicitly(self):
        for kwargs in ({"scan": 0}, {"transfer": -1}, {"inflow": math.nan},
                       {"lower": -1}, {"low1": 14}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Parameters(**kwargs)
        with self.assertRaises(ValueError):
            State(4, 4, v1=2)
        with self.assertRaises(ValueError):
            evolve(State(4, 4), Parameters(), -1)


class ScenarioTests(unittest.TestCase):
    def test_all_six_expected_qualitative_outcomes(self):
        results = {s.name: simulate(s) for s in default_scenarios()}
        for name in ("nominal", "direct-mitigated", "transfer-mitigated"):
            self.assertTrue(results[name]["safe_entire_run"], name)
        for name in ("direct-unmitigated", "transfer-unmitigated", "transfer-late"):
            self.assertFalse(results[name]["safe_entire_run"], name)
        self.assertAlmostEqual(results["direct-unmitigated"]["violation_boundary_time_s"], 14)
        self.assertAlmostEqual(results["transfer-unmitigated"]["violation_boundary_time_s"], 17)

    def test_delayed_mitigation_does_not_erase_earlier_violation(self):
        result = simulate(next(s for s in default_scenarios() if s.name == "transfer-late"))
        self.assertLess(result["violation_boundary_time_s"], result["intervention_at_s"])
        self.assertFalse(result["safe_entire_run"])
        self.assertGreater(result["final_state"]["x2"], Parameters().upper)

    def test_freeze_preserves_levels_even_as_attacker_keeps_overwriting(self):
        result = simulate(Scenario("test", "direct", response_delay=0))
        frozen = [r for r in result["trace"] if r["mitigation_active"]]
        self.assertTrue(frozen)
        self.assertTrue(all(r["v1"] == r["v2"] == r["p2"] == 0 for r in frozen))
        self.assertTrue(all(r["x1"] == frozen[0]["x1"] and r["x2"] == frozen[0]["x2"] for r in frozen))

    def test_scan_alignment_accounts_for_response_latency(self):
        result = simulate(Scenario("off-grid", "direct", attack_at=2.1, response_delay=0.3))
        self.assertEqual(result["attack_started_at_s"], 2.25)
        self.assertEqual(result["intervention_at_s"], 2.75)
        self.assertEqual(result["actual_response_delay_s"], 0.5)

    def test_scan_aligned_boundary_intervention_is_safe(self):
        base = Scenario("boundary", "transfer", response_delay=15,
                        duration=24, initial=State(7, 6, 1))
        self.assertTrue(simulate(base)["safe_entire_run"])
        self.assertFalse(simulate(replace(base, response_delay=15.01))["safe_entire_run"])

    def test_trace_contains_terminal_state_at_partial_last_scan(self):
        result = simulate(Scenario("partial", duration=1.1))
        self.assertEqual(result["trace"][-1]["time_s"], 1.1)
        self.assertIsNone(result["signature_observed_at_s"])

    def test_no_negative_or_nonfinite_time_controls(self):
        for kwargs in ({"duration": 0}, {"attack_at": -1}, {"response_delay": -1},
                       {"duration": math.inf}, {"response_delay": math.nan}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Scenario("bad", **kwargs)

    def test_run_stops_before_leaving_nonnegative_physical_domain(self):
        result = simulate(Scenario("fast-transfer", "transfer", duration=3,
                                   initial=State(7, 6, 1)), Parameters(transfer=100))
        self.assertEqual(result["termination"], "physical-domain-boundary")
        self.assertGreaterEqual(result["min_x1"], 0)
        self.assertLess(result["completed_duration_s"], 3)
        self.assertFalse(result["safe_entire_run"])

    def test_extreme_duration_scan_ratio_is_rejected_without_overflow(self):
        with self.assertRaises(ValueError):
            simulate(Scenario("huge", duration=1e308), Parameters(scan=1e-308))


if __name__ == "__main__":
    unittest.main()
