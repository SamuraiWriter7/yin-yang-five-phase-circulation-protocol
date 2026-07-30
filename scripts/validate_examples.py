#!/usr/bin/env python3
"""Validate Yin-Yang Five-Phase Circulation Protocol v0.2 examples."""

from __future__ import annotations

import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"

PHASES = {"wood", "fire", "earth", "metal", "water"}
GENERATING_EDGES = {
    ("wood", "fire"),
    ("fire", "earth"),
    ("earth", "metal"),
    ("metal", "water"),
    ("water", "wood"),
}
CONTROLLING_EDGES = {
    ("wood", "earth"),
    ("earth", "water"),
    ("water", "fire"),
    ("fire", "metal"),
    ("metal", "wood"),
}
EPSILON = 1e-6

SCHEMA_FILES = {
    # v0.1 records
    "five-phase-state-record":
        SCHEMA_DIR / "five-phase-state-record.schema.json",
    "yin-yang-balance-assessment":
        SCHEMA_DIR / "yin-yang-balance-assessment.schema.json",
    "polarity-shift-receipt":
        SCHEMA_DIR / "polarity-shift-receipt.schema.json",

    # v0.2 records
    "five-phase-transition-policy":
        SCHEMA_DIR / "five-phase-transition-policy.schema.json",
    "phase-transition-evaluation":
        SCHEMA_DIR / "phase-transition-evaluation.schema.json",
    "phase-transition-receipt":
        SCHEMA_DIR / "phase-transition-receipt.schema.json",

    # v0.3 records
    "residual-observation-record":
        SCHEMA_DIR / "residual-observation-record.schema.json",
    "residual-classification-record":
        SCHEMA_DIR / "residual-classification-record.schema.json",
    "residual-recovery-assessment":
        SCHEMA_DIR / "residual-recovery-assessment.schema.json",
    "residual-transformation-receipt":
        SCHEMA_DIR / "residual-transformation-receipt.schema.json",
    "regenerated-value-attribution":
        SCHEMA_DIR / "regenerated-value-attribution.schema.json",
}


class SemanticError(ValueError):
    """Raised when a schema-valid document violates protocol semantics."""


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SemanticError("document root must be a mapping")
    return data


def load_schema(path: Path) -> dict[str, Any]:
    return load_yaml(path)


def document_kind(path: Path) -> str:
    for kind in SCHEMA_FILES:
        if path.name.startswith(f"{kind}."):
            return kind
    raise SemanticError(f"cannot infer schema kind from filename: {path.name}")


def require_close(actual: float, expected: float, label: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=EPSILON):
        raise SemanticError(
            f"{label}: expected {expected:.6f}, got {actual:.6f}"
        )


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def expected_status(
    balance_index: float,
    has_critical_risk: bool,
    minimum: float = 0.8,
    maximum: float = 1.2,
) -> str:
    if has_critical_risk:
        return "unstable"
    if balance_index < minimum:
        return "yin_dominant"
    if balance_index > maximum:
        return "yang_dominant"
    return "balanced"


def validate_five_phase_state(
    data: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> None:
    phase_states = data["phase_states"]
    phases = [item["phase"] for item in phase_states]
    if set(phases) != PHASES or len(phases) != len(set(phases)):
        raise SemanticError(
            "phase_states must contain each of wood, fire, earth, metal, and water exactly once"
        )

    total_yin = sum(float(item["yin_pressure"]) for item in phase_states)
    total_yang = sum(float(item["yang_pressure"]) for item in phase_states)
    balance_index = total_yang / total_yin
    aggregate = data["aggregate"]

    require_close(float(aggregate["total_yin_pressure"]), total_yin, "aggregate.total_yin_pressure")
    require_close(float(aggregate["total_yang_pressure"]), total_yang, "aggregate.total_yang_pressure")
    require_close(float(aggregate["balance_index"]), balance_index, "aggregate.balance_index")

    has_critical_risk = any(float(item["risk_level"]) >= 0.9 for item in phase_states)
    calculated_status = expected_status(balance_index, has_critical_risk)
    if data["status"] != calculated_status:
        raise SemanticError(
            f"status must be '{calculated_status}' for the recorded pressures and risks"
        )

    registry[data["record_id"]] = data


def validate_balance_assessment(
    data: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> None:
    thresholds = data["thresholds"]
    minimum = float(thresholds["minimum_balance_index"])
    maximum = float(thresholds["maximum_balance_index"])
    if minimum >= maximum:
        raise SemanticError("minimum_balance_index must be lower than maximum_balance_index")

    observed = data["observed"]
    total_yin = float(observed["total_yin_pressure"])
    total_yang = float(observed["total_yang_pressure"])
    balance_index = total_yang / total_yin
    require_close(float(observed["balance_index"]), balance_index, "observed.balance_index")

    phase_assessments = data["phase_assessments"]
    phases = [item["phase"] for item in phase_assessments]
    if set(phases) != PHASES or len(phases) != len(set(phases)):
        raise SemanticError("phase_assessments must contain each phase exactly once")

    has_critical = any(
        item["condition"] == "high_risk" or item["severity"] == "critical"
        for item in phase_assessments
    )
    calculated_status = expected_status(balance_index, has_critical, minimum, maximum)
    if data["overall_status"] != calculated_status:
        raise SemanticError(f"overall_status must be '{calculated_status}'")

    state_ref = data["state_record_ref"]
    state = registry.get(state_ref)
    if state is None:
        raise SemanticError(f"state_record_ref does not resolve: {state_ref}")
    if state["cycle_id"] != data["cycle_id"]:
        raise SemanticError("cycle_id must match the referenced state record")

    state_aggregate = state["aggregate"]
    require_close(total_yin, float(state_aggregate["total_yin_pressure"]), "assessment/state total_yin_pressure")
    require_close(total_yang, float(state_aggregate["total_yang_pressure"]), "assessment/state total_yang_pressure")
    require_close(balance_index, float(state_aggregate["balance_index"]), "assessment/state balance_index")

    registry[data["assessment_id"]] = data


def comparator_holds(observed: float, comparator: str, threshold: float) -> bool:
    return {
        "gt": observed > threshold,
        "gte": observed >= threshold,
        "lt": observed < threshold,
        "lte": observed <= threshold,
        "eq": math.isclose(observed, threshold, rel_tol=0.0, abs_tol=EPSILON),
    }[comparator]


def validate_polarity_shift(
    data: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> None:
    if data["previous_polarity"] == data["new_polarity"]:
        raise SemanticError("previous_polarity and new_polarity must differ")

    for trigger in data["triggers"]:
        if not comparator_holds(
            float(trigger["observed_value"]),
            trigger["comparator"],
            float(trigger["threshold"]),
        ):
            raise SemanticError(
                f"trigger condition is not satisfied for metric '{trigger['metric']}'"
            )

    yin_actions = {
        "reduce_load", "route_workload", "hold_resources", "activate_cooling",
        "throttle_growth", "quarantine_residual", "review_dormant_residual",
    }
    yang_actions = {
        "increase_load", "route_workload", "release_resources",
        "activate_recovery", "stimulate_growth",
    }
    action_types = {action["action_type"] for action in data["actions"]}
    required_family = yin_actions if data["new_polarity"] == "yin" else yang_actions
    if action_types.isdisjoint(required_family):
        raise SemanticError(
            f"a shift to {data['new_polarity']} requires at least one compatible action"
        )

    result_status = data["result"]["status"]
    if result_status in {"applied", "stabilized"}:
        if data["authorization"]["decision"] != "authorized":
            raise SemanticError("applied or stabilized shifts require authorization")
        if "effective_at" not in data:
            raise SemanticError("applied or stabilized shifts require effective_at")

    state = registry.get(data["state_record_ref"])
    assessment = registry.get(data["assessment_ref"])
    if state is None:
        raise SemanticError(f"state_record_ref does not resolve: {data['state_record_ref']}")
    if assessment is None:
        raise SemanticError(f"assessment_ref does not resolve: {data['assessment_ref']}")
    if state["cycle_id"] != data["cycle_id"] or assessment["cycle_id"] != data["cycle_id"]:
        raise SemanticError("cycle_id must match both referenced records")
    if assessment["state_record_ref"] != data["state_record_ref"]:
        raise SemanticError("assessment_ref must assess the referenced state record")

    phase_state = next(item for item in state["phase_states"] if item["phase"] == data["phase"])
    if phase_state["polarity"] != data["previous_polarity"]:
        raise SemanticError("previous_polarity must match the referenced phase state")

    registry[data["shift_id"]] = data


def edge_set(items: list[dict[str, Any]]) -> set[tuple[str, str]]:
    return {(item["source_phase"], item["target_phase"]) for item in items}


def validate_transition_policy(
    data: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> None:
    generating = edge_set(data["generating_cycle"])
    controlling = edge_set(data["controlling_cycle"])
    if generating != GENERATING_EDGES:
        missing = sorted(GENERATING_EDGES - generating)
        extra = sorted(generating - GENERATING_EDGES)
        raise SemanticError(
            f"generating_cycle must match the canonical cycle; missing={missing}, extra={extra}"
        )
    if controlling != CONTROLLING_EDGES:
        missing = sorted(CONTROLLING_EDGES - controlling)
        extra = sorted(controlling - CONTROLLING_EDGES)
        raise SemanticError(
            f"controlling_cycle must match the canonical cycle; missing={missing}, extra={extra}"
        )

    blocked = edge_set(data["blocked_transitions"])
    review = edge_set(data["human_review_transitions"])
    if blocked & (GENERATING_EDGES | CONTROLLING_EDGES):
        raise SemanticError("blocked_transitions must not contradict canonical relations")
    if not review <= (GENERATING_EDGES | CONTROLLING_EDGES):
        raise SemanticError("human_review_transitions must reference canonical relations")
    if blocked & review:
        raise SemanticError("a transition cannot be both blocked and human-review-required")

    registry[data["policy_id"]] = data


def relation_for(policy: dict[str, Any], edge: tuple[str, str]) -> str:
    if edge in edge_set(policy["generating_cycle"]):
        return "generating"
    if edge in edge_set(policy["controlling_cycle"]):
        return "controlling"
    return "none"


def expected_transition_decision(
    data: dict[str, Any], policy: dict[str, Any]
) -> tuple[str, str, int, bool]:
    edge = (data["source_phase"], data["target_phase"])
    relation = relation_for(policy, edge)
    blocked = edge in edge_set(policy["blocked_transitions"])
    review = edge in edge_set(policy["human_review_transitions"])

    if blocked or relation == "none":
        return "denied", relation, 0, True

    cooldown_key = (
        "generating_default_seconds"
        if relation == "generating"
        else "controlling_default_seconds"
    )
    required = int(policy["cooldown_policy"][cooldown_key])
    timing = data["timing"]
    elapsed = int(timing["elapsed_seconds"])
    cooldown_satisfied = elapsed >= required
    emergency_bypass = (
        data["emergency"]
        and policy["cooldown_policy"]["emergency_bypass_allowed"]
    )

    if review:
        return "human_review_required", relation, required, cooldown_satisfied
    if not cooldown_satisfied and not emergency_bypass:
        return "denied", relation, required, False
    return "allowed", relation, required, cooldown_satisfied


def validate_transition_evaluation(
    data: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> None:
    state = registry.get(data["state_record_ref"])
    assessment = registry.get(data["assessment_ref"])
    policy = registry.get(data["policy_ref"])
    if state is None:
        raise SemanticError(f"state_record_ref does not resolve: {data['state_record_ref']}")
    if assessment is None:
        raise SemanticError(f"assessment_ref does not resolve: {data['assessment_ref']}")
    if policy is None:
        raise SemanticError(f"policy_ref does not resolve: {data['policy_ref']}")
    if state["cycle_id"] != data["cycle_id"] or assessment["cycle_id"] != data["cycle_id"]:
        raise SemanticError("cycle_id must match the referenced state and assessment")
    if assessment["state_record_ref"] != data["state_record_ref"]:
        raise SemanticError("assessment_ref must assess the referenced state record")

    source_state = next(
        item for item in state["phase_states"] if item["phase"] == data["source_phase"]
    )
    if source_state["polarity"] != data["source_polarity"]:
        raise SemanticError("source_polarity must match the referenced source phase state")
    if data["source_phase"] == data["target_phase"]:
        raise SemanticError("source_phase and target_phase must differ")

    timing = data["timing"]
    calculated_elapsed = int(
        (parse_dt(timing["requested_at"]) - parse_dt(timing["last_transition_at"])).total_seconds()
    )
    if calculated_elapsed < 0:
        raise SemanticError("requested_at must not precede last_transition_at")
    if int(timing["elapsed_seconds"]) != calculated_elapsed:
        raise SemanticError(
            f"elapsed_seconds must equal timestamp difference ({calculated_elapsed})"
        )

    expected_decision, expected_relation, required, cooldown_satisfied = (
        expected_transition_decision(data, policy)
    )
    if data["relation_type"] != expected_relation:
        raise SemanticError(f"relation_type must be '{expected_relation}'")
    if int(timing["required_cooldown_seconds"]) != required:
        raise SemanticError(
            f"required_cooldown_seconds must be {required} for {expected_relation}"
        )
    if bool(timing["cooldown_satisfied"]) != cooldown_satisfied:
        raise SemanticError(
            f"cooldown_satisfied must be {str(cooldown_satisfied).lower()}"
        )
    if data["decision"] != expected_decision:
        raise SemanticError(f"decision must be '{expected_decision}'")

    reasons = set(data["reason_codes"])
    edge = (data["source_phase"], data["target_phase"])
    if expected_relation == "generating" and "canonical_generating_relation" not in reasons:
        raise SemanticError("canonical generating transitions require its reason code")
    if expected_relation == "controlling" and "canonical_controlling_relation" not in reasons:
        raise SemanticError("canonical controlling transitions require its reason code")
    if edge in edge_set(policy["blocked_transitions"]) and "blocked_by_policy" not in reasons:
        raise SemanticError("blocked transitions require blocked_by_policy")
    if expected_relation == "none" and edge not in edge_set(policy["blocked_transitions"]) and "noncanonical_path" not in reasons:
        raise SemanticError("noncanonical transitions require noncanonical_path")
    if expected_decision == "human_review_required" and "human_review_policy" not in reasons:
        raise SemanticError("review-required transitions require human_review_policy")
    if cooldown_satisfied and expected_relation != "none" and "cooldown_satisfied" not in reasons:
        raise SemanticError("satisfied cooldown requires cooldown_satisfied reason code")
    if not cooldown_satisfied and not data["emergency"] and "cooldown_not_satisfied" not in reasons:
        raise SemanticError("unsatisfied cooldown requires cooldown_not_satisfied")
    if data["emergency"] and not cooldown_satisfied and "emergency_bypass" not in reasons:
        raise SemanticError("emergency cooldown bypass requires emergency_bypass")

    registry[data["evaluation_id"]] = data


def validate_transition_receipt(
    data: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> None:
    evaluation = registry.get(data["evaluation_ref"])
    policy = registry.get(data["policy_ref"])
    if evaluation is None:
        raise SemanticError(f"evaluation_ref does not resolve: {data['evaluation_ref']}")
    if policy is None:
        raise SemanticError(f"policy_ref does not resolve: {data['policy_ref']}")

    fields = [
        "cycle_id", "policy_ref", "source_phase", "target_phase",
        "source_polarity", "target_polarity", "relation_type",
    ]
    for field in fields:
        if data[field] != evaluation[field]:
            raise SemanticError(f"{field} must match the referenced evaluation")

    if data["authorization"]["policy_ref"] != data["policy_ref"]:
        raise SemanticError("authorization.policy_ref must match policy_ref")

    result_status = data["result"]["status"]
    authorization = data["authorization"]["decision"]
    evaluation_decision = evaluation["decision"]

    if result_status in {"applied", "completed"}:
        if evaluation_decision not in {"allowed", "human_review_required"}:
            raise SemanticError("applied or completed transitions require an approvable evaluation")
        if authorization != "authorized":
            raise SemanticError("applied or completed transitions require authorization")
        if "effective_at" not in data:
            raise SemanticError("applied or completed transitions require effective_at")

    if evaluation_decision == "denied" and result_status not in {"rejected", "pending"}:
        raise SemanticError("a denied evaluation may only produce a rejected or pending receipt")

    if result_status == "rejected" and authorization == "authorized":
        raise SemanticError("a rejected transition must not be authorized")

    registry[data["transition_id"]] = data


SEMANTIC_VALIDATORS: dict[
    str,
    Callable[[dict[str, Any], dict[str, dict[str, Any]]], None],
] = {
    "five-phase-state-record": validate_five_phase_state,
    "yin-yang-balance-assessment": validate_balance_assessment,
    "polarity-shift-receipt": validate_polarity_shift,
    "five-phase-transition-policy": validate_transition_policy,
    "phase-transition-evaluation": validate_transition_evaluation,
    "phase-transition-receipt": validate_transition_receipt,
}


def schema_errors(
    validator: Draft202012Validator, data: dict[str, Any]
) -> list[str]:
    errors = sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path))
    return [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]


def validate_pass_examples(
    validators: dict[str, Draft202012Validator],
) -> tuple[bool, dict[str, dict[str, Any]]]:
    registry: dict[str, dict[str, Any]] = {}
    ok = True
    for kind in SCHEMA_FILES:
        for path in sorted(PASS_DIR.glob(f"{kind}.*.yaml")):
            print(f"\n[validate-pass] {path.relative_to(ROOT)}")
            data = load_yaml(path)
            errors = schema_errors(validators[kind], data)
            if errors:
                ok = False
                print("[schema-error]")
                for message in errors:
                    print(f"  - {message}")
                continue
            print("[schema-ok]")
            try:
                SEMANTIC_VALIDATORS[kind](data, registry)
            except SemanticError as exc:
                ok = False
                print("[semantic-error]")
                print(f"  - {exc}")
            else:
                print("[semantic-ok]")
    return ok, registry


def validate_fail_examples(
    validators: dict[str, Draft202012Validator],
    pass_registry: dict[str, dict[str, Any]],
) -> bool:
    ok = True
    for path in sorted(FAIL_DIR.glob("*.yaml")):
        kind = document_kind(path)
        print(f"\n[validate-fail] {path.relative_to(ROOT)}")
        data = load_yaml(path)
        errors = schema_errors(validators[kind], data)
        if errors:
            print("[expected-schema-failure]")
            for message in errors:
                print(f"  - {message}")
            continue
        isolated_registry = dict(pass_registry)
        try:
            SEMANTIC_VALIDATORS[kind](data, isolated_registry)
        except SemanticError as exc:
            print("[expected-semantic-failure]")
            print(f"  - {exc}")
        else:
            ok = False
            print("[unexpected-pass]")
            print("  - fail example passed both schema and semantic validation")
    return ok


def main() -> int:
    print("=== Yin-Yang Five-Phase Circulation Protocol v0.2 Validation ===")
    validators: dict[str, Draft202012Validator] = {}
    for kind, schema_path in SCHEMA_FILES.items():
        schema = load_schema(schema_path)
        Draft202012Validator.check_schema(schema)
        validators[kind] = Draft202012Validator(
            schema, format_checker=FormatChecker()
        )
        print(f"schema [{kind}]: {schema_path.relative_to(ROOT)}")

    pass_ok, registry = validate_pass_examples(validators)
    fail_ok = validate_fail_examples(validators, registry)
    if pass_ok and fail_ok:
        print("\nValidation succeeded.")
        return 0
    print("\nValidation failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
