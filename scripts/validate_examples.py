#!/usr/bin/env python3
"""Validate Yin-Yang Five-Phase Circulation Protocol v0.5 examples."""

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
    "five-phase-state-record": SCHEMA_DIR / "five-phase-state-record.schema.json",
    "yin-yang-balance-assessment": SCHEMA_DIR / "yin-yang-balance-assessment.schema.json",
    "polarity-shift-receipt": SCHEMA_DIR / "polarity-shift-receipt.schema.json",
    "five-phase-transition-policy": SCHEMA_DIR / "five-phase-transition-policy.schema.json",
    "phase-transition-evaluation": SCHEMA_DIR / "phase-transition-evaluation.schema.json",
    "phase-transition-receipt": SCHEMA_DIR / "phase-transition-receipt.schema.json",
    "residual-observation-record": (
        SCHEMA_DIR / "residual-observation-record.schema.json"
    ),
    "residual-classification-record": (
        SCHEMA_DIR / "residual-classification-record.schema.json"
    ),
    "residual-recovery-assessment": (
        SCHEMA_DIR / "residual-recovery-assessment.schema.json"
    ),
    "residual-transformation-receipt": (
        SCHEMA_DIR / "residual-transformation-receipt.schema.json"
    ),
    "regenerated-value-attribution": (
        SCHEMA_DIR / "regenerated-value-attribution.schema.json"
    ),
    "circulation-governor-delegation": (
        SCHEMA_DIR / "circulation-governor-delegation.schema.json"
    ),
    "federated-balance-assessment": (
        SCHEMA_DIR / "federated-balance-assessment.schema.json"
    ),
    "federated-rebalancing-plan": (
        SCHEMA_DIR / "federated-rebalancing-plan.schema.json"
    ),
    "rebalancing-conflict-resolution": (
        SCHEMA_DIR / "rebalancing-conflict-resolution.schema.json"
    ),
    "federated-rebalancing-receipt": (
        SCHEMA_DIR / "federated-rebalancing-receipt.schema.json"
    ),
    "civilization-os-interoperability-profile": (
        SCHEMA_DIR / "civilization-os-interoperability-profile.schema.json"
    ),
    "circulation-operation-binding": (
        SCHEMA_DIR / "circulation-operation-binding.schema.json"
    ),
    "circulation-execution-evidence": (
        SCHEMA_DIR / "circulation-execution-evidence.schema.json"
    ),
    "circulation-audit-record": (
        SCHEMA_DIR / "circulation-audit-record.schema.json"
    ),
    "circulation-royalty-settlement-receipt": (
        SCHEMA_DIR / "circulation-royalty-settlement-receipt.schema.json"
    ),
    "civilization-os-conformance-assessment": (
        SCHEMA_DIR / "civilization-os-conformance-assessment.schema.json"
    ),
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



def resolve_record(
    registry: dict[str, dict[str, Any]],
    reference: str,
    label: str,
) -> dict[str, Any]:
    record = registry.get(reference)

    if record is None:
        raise SemanticError(
            f"{label} does not resolve: {reference}"
        )

    return record


def validate_residual_observation(
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    if (
        data["containment_level"] == "quarantined"
        and "content_fingerprint" not in data
    ):
        raise SemanticError(
            "quarantined residuals require content_fingerprint"
        )

    registry[data["observation_id"]] = data


def validate_residual_classification(
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    observation = resolve_record(
        registry,
        data["observation_ref"],
        "observation_ref",
    )

    if observation["cycle_id"] != data["cycle_id"]:
        raise SemanticError(
            "cycle_id must match the referenced observation"
        )

    classification = data["classification"]
    has_targets = bool(data.get("candidate_target_phases"))
    has_vault = "vault_ref" in data
    has_review = "review_after" in data
    has_quarantine = "quarantine_ref" in data

    if classification == "recoverable":
        if not has_targets:
            raise SemanticError(
                "recoverable classification requires "
                "candidate_target_phases"
            )

        if has_vault or has_quarantine:
            raise SemanticError(
                "recoverable classification cannot include "
                "vault_ref or quarantine_ref"
            )

    elif classification == "dormant":
        if not has_vault or not has_review:
            raise SemanticError(
                "dormant classification requires "
                "vault_ref and review_after"
            )

        if has_targets or has_quarantine:
            raise SemanticError(
                "dormant classification cannot be routed "
                "or quarantined"
            )

    elif classification == "hazardous":
        if not has_quarantine:
            raise SemanticError(
                "hazardous classification requires quarantine_ref"
            )

        if has_targets or has_vault:
            raise SemanticError(
                "hazardous classification cannot include "
                "an active route or vault_ref"
            )

        if data.get("sanitization_required") is not True:
            raise SemanticError(
                "hazardous classification requires "
                "sanitization_required: true"
            )

        if observation["containment_level"] == "open":
            raise SemanticError(
                "hazardous residuals cannot remain open"
            )

    registry[data["classification_id"]] = data


def validate_residual_recovery_assessment(
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    observation = resolve_record(
        registry,
        data["observation_ref"],
        "observation_ref",
    )
    classification = resolve_record(
        registry,
        data["classification_ref"],
        "classification_ref",
    )
    state_record = resolve_record(
        registry,
        data["state_record_ref"],
        "state_record_ref",
    )
    transition_policy = resolve_record(
        registry,
        data["transition_policy_ref"],
        "transition_policy_ref",
    )

    if any(
        record["cycle_id"] != data["cycle_id"]
        for record in (
            observation,
            classification,
            state_record,
        )
    ):
        raise SemanticError(
            "cycle_id must match observation, classification, "
            "and state records"
        )

    if classification["observation_ref"] != data["observation_ref"]:
        raise SemanticError(
            "classification_ref must classify "
            "the referenced observation"
        )

    if classification["classification"] != "recoverable":
        raise SemanticError(
            "recovery assessment requires "
            "a recoverable classification"
        )

    phase_route = data["phase_route"]

    if phase_route[0] != observation["source_phase"]:
        raise SemanticError(
            "phase_route must begin with "
            "the observation source_phase"
        )

    if (
        phase_route[-1]
        not in classification["candidate_target_phases"]
    ):
        raise SemanticError(
            "phase_route must end in a candidate_target_phase"
        )

    generating_edges = {
        (
            edge["source_phase"],
            edge["target_phase"],
        )
        for edge in transition_policy["generating_cycle"]
    }
    controlling_edges = {
        (
            edge["source_phase"],
            edge["target_phase"],
        )
        for edge in transition_policy["controlling_cycle"]
    }
    blocked_edges = {
        (
            edge["source_phase"],
            edge["target_phase"],
        )
        for edge in transition_policy["blocked_transitions"]
    }

    route_edges = list(
        zip(
            phase_route,
            phase_route[1:],
        )
    )

    route_valid = all(
        edge in generating_edges | controlling_edges
        and edge not in blocked_edges
        for edge in route_edges
    )

    valuation = data["valuation"]

    gross_adjusted_value = (
        float(valuation["converted_utility"])
        * float(valuation["recovery_efficiency"])
        * float(valuation["temporal_fit"])
        * float(valuation["spatial_fit"])
        * float(valuation["trust_factor"])
    )

    net_residual_value = gross_adjusted_value - (
        float(valuation["collection_cost"])
        + float(valuation["conversion_cost"])
        + float(valuation["risk_cost"])
    )

    require_close(
        float(valuation["gross_adjusted_value"]),
        gross_adjusted_value,
        "valuation.gross_adjusted_value",
    )
    require_close(
        float(valuation["net_residual_value"]),
        net_residual_value,
        "valuation.net_residual_value",
    )

    thresholds = data["thresholds"]
    net_value_sufficient = (
        net_residual_value
        >= float(thresholds["minimum_net_value"])
    )
    trust_sufficient = (
        float(valuation["trust_factor"])
        >= float(thresholds["minimum_trust_factor"])
    )

    if (
        not route_valid
        or not net_value_sufficient
        or not trust_sufficient
    ):
        expected_decision = "not_viable"
    elif data["authorization_requirement"] == "human":
        expected_decision = "human_review_required"
    else:
        expected_decision = "viable"

    if data["decision"] != expected_decision:
        raise SemanticError(
            f"decision must be '{expected_decision}'"
        )

    registry[data["assessment_id"]] = data


def validate_residual_transformation(
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    observation = resolve_record(
        registry,
        data["observation_ref"],
        "observation_ref",
    )
    classification = resolve_record(
        registry,
        data["classification_ref"],
        "classification_ref",
    )
    recovery_assessment = resolve_record(
        registry,
        data["recovery_assessment_ref"],
        "recovery_assessment_ref",
    )

    if any(
        record["cycle_id"] != data["cycle_id"]
        for record in (
            observation,
            classification,
            recovery_assessment,
        )
    ):
        raise SemanticError(
            "cycle_id must match all referenced R2R records"
        )

    if (
        recovery_assessment["observation_ref"]
        != data["observation_ref"]
    ):
        raise SemanticError(
            "recovery assessment must reference "
            "the same observation"
        )

    if (
        recovery_assessment["classification_ref"]
        != data["classification_ref"]
    ):
        raise SemanticError(
            "recovery assessment must reference "
            "the same classification"
        )

    if data["phase_route"] != recovery_assessment["phase_route"]:
        raise SemanticError(
            "phase_route must match the recovery assessment"
        )

    result_status = data["result"]["status"]

    if result_status in {"completed", "partial"}:
        if recovery_assessment["decision"] != "viable":
            raise SemanticError(
                "completed or partial transformation "
                "requires a viable assessment"
            )

        if data["authorization"]["decision"] != "authorized":
            raise SemanticError(
                "completed or partial transformation "
                "requires authorization"
            )

        if "completed_at" not in data:
            raise SemanticError(
                "completed or partial transformation "
                "requires completed_at"
            )

        if not data.get("output_resources"):
            raise SemanticError(
                "completed or partial transformation "
                "requires output_resources"
            )

        final_phase = data["phase_route"][-1]

        for output in data["output_resources"]:
            if output["target_phase"] != final_phase:
                raise SemanticError(
                    "output resource target_phase must match "
                    "the final phase_route phase"
                )

    accounting = data["value_accounting"]
    input_value = float(accounting["input_equivalent_value"])
    output_value = float(accounting["output_equivalent_value"])
    loss_value = float(accounting["conversion_loss_value"])
    unallocated_value = float(accounting["unallocated_value"])

    require_close(
        input_value,
        output_value + loss_value + unallocated_value,
        "value conservation",
    )

    assessed_valuation = recovery_assessment["valuation"]

    require_close(
        input_value,
        float(assessed_valuation["gross_adjusted_value"]),
        "input/assessment gross value",
    )

    assessed_net_value = float(
        assessed_valuation["net_residual_value"]
    )

    if output_value - assessed_net_value > EPSILON:
        raise SemanticError(
            "output_equivalent_value cannot exceed "
            "assessed net_residual_value"
        )

    if result_status == "completed":
        require_close(
            output_value,
            assessed_net_value,
            "completed output/net value",
        )

    registry[data["transformation_id"]] = data


def validate_regenerated_value_attribution(
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    transformation = resolve_record(
        registry,
        data["transformation_ref"],
        "transformation_ref",
    )
    observation = resolve_record(
        registry,
        data["source_observation_ref"],
        "source_observation_ref",
    )

    if (
        transformation["cycle_id"] != data["cycle_id"]
        or observation["cycle_id"] != data["cycle_id"]
    ):
        raise SemanticError(
            "cycle_id must match transformation and observation"
        )

    if (
        transformation["observation_ref"]
        != data["source_observation_ref"]
    ):
        raise SemanticError(
            "source_observation_ref must match "
            "the transformation observation"
        )

    if transformation["result"]["status"] not in {
        "completed",
        "partial",
    }:
        raise SemanticError(
            "attribution requires a completed "
            "or partial transformation"
        )

    for record in registry.values():
        if (
            record.get("value_accounting_key")
            == data["value_accounting_key"]
        ):
            raise SemanticError(
                "value_accounting_key must be unique"
            )

    contribution_total = sum(
        float(item["contribution_weight"])
        for item in data["origin_contributions"]
    )
    share_total = sum(
        float(item["share_ratio"])
        for item in data["allocations"]
    )
    allocation_total = sum(
        float(item["amount"])
        for item in data["allocations"]
    )
    regenerated_value = float(
        data["regenerated_value"]["amount"]
    )

    require_close(
        contribution_total,
        1.0,
        "origin contribution weights",
    )
    require_close(
        share_total,
        1.0,
        "allocation share ratios",
    )
    require_close(
        allocation_total,
        regenerated_value,
        "allocation amounts",
    )

    transformed_output = float(
        transformation["value_accounting"]
        ["output_equivalent_value"]
    )

    if regenerated_value - transformed_output > EPSILON:
        raise SemanticError(
            "regenerated value cannot exceed "
            "transformed output value"
        )

    if (
        data["royalty_status"] == "settled"
        and "royalty_ledger_ref" not in data
    ):
        raise SemanticError(
            "settled attribution requires royalty_ledger_ref"
        )

    registry[data["attribution_id"]] = data



def validate_governor_delegation(
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    valid_from = parse_dt(data["valid_from"])
    valid_until = parse_dt(data["valid_until"])
    issued_at = parse_dt(data["issued_at"])

    if valid_until <= valid_from:
        raise SemanticError("valid_until must be later than valid_from")

    if data["status"] == "active" and not (
        valid_from <= issued_at <= valid_until
    ):
        raise SemanticError(
            "active delegation issued_at must fall within its validity window"
        )

    scope = data["authority_scope"]
    if scope["emergency_authority"] and (
        "emergency_rebalance" not in scope["allowed_actions"]
    ):
        raise SemanticError(
            "emergency authority requires emergency_rebalance action"
        )

    registry[data["delegation_id"]] = data


def validate_federated_balance_assessment(
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    members = data["member_states"]
    member_ids = [item["member_id"] for item in members]

    if len(member_ids) != len(set(member_ids)):
        raise SemanticError("member_states must use unique member_id values")

    for member in members:
        state = resolve_record(
            registry,
            member["state_record_ref"],
            "state_record_ref",
        )
        require_close(
            float(member["balance_index"]),
            float(state["aggregate"]["balance_index"]),
            f"member {member['member_id']} balance_index",
        )
        maximum_risk = max(
            float(item["risk_level"])
            for item in state["phase_states"]
        )
        require_close(
            float(member["risk_level"]),
            maximum_risk,
            f"member {member['member_id']} risk_level",
        )

    total_export = sum(
        float(item["available_export_capacity"])
        for item in members
    )
    total_unmet = sum(float(item["unmet_demand"]) for item in members)
    maximum_risk = max(float(item["risk_level"]) for item in members)
    totals = data["federation_totals"]

    require_close(
        float(totals["available_export_capacity"]),
        total_export,
        "federation_totals.available_export_capacity",
    )
    require_close(
        float(totals["unmet_demand"]),
        total_unmet,
        "federation_totals.unmet_demand",
    )
    require_close(
        float(totals["net_capacity"]),
        total_export - total_unmet,
        "federation_totals.net_capacity",
    )
    require_close(
        float(totals["maximum_member_risk"]),
        maximum_risk,
        "federation_totals.maximum_member_risk",
    )

    imbalance_members = {item["member_id"] for item in data["imbalances"]}
    unknown_members = imbalance_members - set(member_ids)
    if unknown_members:
        raise SemanticError(
            f"imbalances reference unknown members: {sorted(unknown_members)}"
        )

    if maximum_risk >= 0.98 or total_export + EPSILON < total_unmet:
        expected = "federation_unstable"
    elif maximum_risk >= 0.90 or total_unmet > EPSILON:
        expected = "localized_imbalance"
    else:
        expected = "balanced"

    if data["overall_status"] != expected:
        raise SemanticError(f"overall_status must be '{expected}'")

    registry[data["assessment_id"]] = data


def validate_federated_rebalancing_plan(
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    assessment = resolve_record(
        registry, data["assessment_ref"], "assessment_ref"
    )
    delegation = resolve_record(
        registry, data["delegation_ref"], "delegation_ref"
    )

    if assessment["federation_id"] != data["federation_id"]:
        raise SemanticError("federation_id must match assessment_ref")
    if delegation["federation_id"] != data["federation_id"]:
        raise SemanticError("federation_id must match delegation_ref")
    if assessment["epoch_id"] != data["epoch_id"]:
        raise SemanticError("epoch_id must match assessment_ref")
    if delegation["governor_ref"] != data["governor_ref"]:
        raise SemanticError("governor_ref must match delegated governor")
    if delegation["status"] != "active":
        raise SemanticError("rebalancing plan requires an active delegation")

    created_at = parse_dt(data["created_at"])
    if not (
        parse_dt(delegation["valid_from"])
        <= created_at
        <= parse_dt(delegation["valid_until"])
    ):
        raise SemanticError(
            "created_at must fall within the delegation validity window"
        )

    scope = delegation["authority_scope"]
    required_action = (
        "emergency_rebalance" if data["emergency"] else "propose_rebalance"
    )
    if required_action not in scope["allowed_actions"]:
        raise SemanticError(
            f"delegation does not allow {required_action}"
        )
    if data["emergency"]:
        if not scope["emergency_authority"]:
            raise SemanticError("emergency plan requires emergency authority")
        if "emergency_reason" not in data:
            raise SemanticError("emergency plan requires emergency_reason")

    members = {
        item["member_id"]: item for item in assessment["member_states"]
    }
    transfer_ids = [item["transfer_id"] for item in data["transfer_candidates"]]
    if len(transfer_ids) != len(set(transfer_ids)):
        raise SemanticError("transfer_candidates must use unique transfer_id values")

    totals_by_source: dict[str, float] = {}
    for transfer in data["transfer_candidates"]:
        source_id = transfer["source_member_id"]
        target_id = transfer["target_member_id"]
        if source_id == target_id:
            raise SemanticError("source_member_id and target_member_id must differ")
        if source_id not in members or target_id not in members:
            raise SemanticError("transfer candidate references an unknown member")

        source = members[source_id]
        target = members[target_id]
        if source["region"] not in scope["regions"] or target["region"] not in scope["regions"]:
            raise SemanticError("transfer candidate is outside delegated regions")
        scoped_members = set(scope.get("members", []))
        if scoped_members and (
            source_id not in scoped_members or target_id not in scoped_members
        ):
            raise SemanticError("transfer candidate is outside delegated members")
        if (
            transfer["source_phase"] not in scope["phases"]
            or transfer["target_phase"] not in scope["phases"]
        ):
            raise SemanticError("transfer candidate is outside delegated phases")

        totals_by_source[source_id] = totals_by_source.get(source_id, 0.0) + float(
            transfer["amount"]
        )

    for source_id, amount in totals_by_source.items():
        allowed = (
            float(members[source_id]["available_export_capacity"])
            * float(scope["maximum_transfer_ratio"])
        )
        if amount - allowed > EPSILON:
            raise SemanticError(
                f"planned transfers from {source_id} exceed delegated capacity ratio"
            )

    known_transfers = set(transfer_ids)
    conflict_ids: list[str] = []
    for group in data["conflict_groups"]:
        conflict_ids.append(group["conflict_group_id"])
        unknown = set(group["transfer_ids"]) - known_transfers
        if unknown:
            raise SemanticError(
                f"conflict group references unknown transfers: {sorted(unknown)}"
            )
    if len(conflict_ids) != len(set(conflict_ids)):
        raise SemanticError("conflict_groups must use unique conflict_group_id values")

    expected_status = (
        "ready_for_resolution" if data["conflict_groups"] else "ready"
    )
    if data["status"] != expected_status:
        raise SemanticError(f"status must be '{expected_status}'")

    registry[data["plan_id"]] = data


def validate_rebalancing_conflict_resolution(
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    plan = resolve_record(registry, data["plan_ref"], "plan_ref")
    delegation = resolve_record(
        registry, data["delegation_ref"], "delegation_ref"
    )

    if plan["federation_id"] != data["federation_id"]:
        raise SemanticError("federation_id must match plan_ref")
    if delegation["federation_id"] != data["federation_id"]:
        raise SemanticError("federation_id must match delegation_ref")
    if "resolve_conflict" not in delegation["authority_scope"]["allowed_actions"]:
        raise SemanticError("delegation does not allow conflict resolution")

    group = next(
        (
            item for item in plan["conflict_groups"]
            if item["conflict_group_id"] == data["conflict_group_id"]
        ),
        None,
    )
    if group is None:
        raise SemanticError("conflict_group_id does not resolve in plan")

    competing = set(data["competing_transfer_refs"])
    if competing != set(group["transfer_ids"]):
        raise SemanticError(
            "competing_transfer_refs must match the plan conflict group"
        )

    selected = set(data["selected_transfer_refs"])
    rejected = set(data["rejected_transfer_refs"])
    if selected & rejected:
        raise SemanticError(
            "selected and rejected transfer references must be disjoint"
        )
    if selected | rejected != competing:
        raise SemanticError(
            "selected and rejected transfers must partition competing transfers"
        )

    if data["decision"] == "resolved" and not selected:
        raise SemanticError("resolved conflict requires a selected transfer")

    registry[data["resolution_id"]] = data


def validate_federated_rebalancing_receipt(
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    plan = resolve_record(registry, data["plan_ref"], "plan_ref")
    delegation = resolve_record(
        registry, data["delegation_ref"], "delegation_ref"
    )

    for field in ("federation_id", "epoch_id", "delegation_ref", "emergency"):
        if data[field] != plan[field]:
            raise SemanticError(f"{field} must match the referenced plan")

    if delegation["federation_id"] != data["federation_id"]:
        raise SemanticError("delegation federation_id must match receipt")

    resolutions = [
        resolve_record(registry, ref, "conflict_resolution_ref")
        for ref in data["conflict_resolution_refs"]
    ]
    if any(item["plan_ref"] != data["plan_ref"] for item in resolutions):
        raise SemanticError("all conflict resolutions must reference the same plan")

    resolution_by_group = {
        item["conflict_group_id"]: item for item in resolutions
    }
    plan_groups = {
        item["conflict_group_id"]: item for item in plan["conflict_groups"]
    }
    if set(resolution_by_group) != set(plan_groups):
        raise SemanticError(
            "receipt must resolve every conflict group exactly once"
        )

    rejected: set[str] = set()
    selected: set[str] = set()
    for resolution in resolutions:
        if resolution["decision"] != "resolved":
            raise SemanticError("receipt requires resolved conflicts")
        rejected.update(resolution["rejected_transfer_refs"])
        selected.update(resolution["selected_transfer_refs"])

    conflict_members = {
        transfer_id
        for group in plan["conflict_groups"]
        for transfer_id in group["transfer_ids"]
    }
    all_candidates = {
        item["transfer_id"]: item for item in plan["transfer_candidates"]
    }
    approved = (set(all_candidates) - conflict_members) | selected

    executed = data["executed_transfers"]
    executed_ids = [item["transfer_ref"] for item in executed]
    if len(executed_ids) != len(set(executed_ids)):
        raise SemanticError("executed_transfers must use unique transfer_ref values")
    if set(executed_ids) & rejected:
        raise SemanticError("receipt cannot execute a rejected transfer")
    if not set(executed_ids) <= approved:
        raise SemanticError("receipt executes an unapproved transfer")

    for item in executed:
        planned = all_candidates[item["transfer_ref"]]
        if item["unit"] != planned["unit"]:
            raise SemanticError("executed transfer unit must match the plan")
        if float(item["executed_amount"]) - float(planned["amount"]) > EPSILON:
            raise SemanticError("executed_amount cannot exceed planned amount")

    status = data["result"]["status"]
    if status in {"applied", "completed", "partial"}:
        if data["authorization"]["decision"] != "authorized":
            raise SemanticError(
                "applied, completed, or partial receipt requires authorization"
            )
    if status == "completed":
        if set(executed_ids) != approved:
            raise SemanticError(
                "completed receipt must execute every approved transfer"
            )
        if "completed_at" not in data:
            raise SemanticError("completed receipt requires completed_at")

    if data["emergency"]:
        scope = delegation["authority_scope"]
        if not scope["emergency_authority"]:
            raise SemanticError("emergency receipt requires emergency authority")
        if "emergency_rebalance" not in scope["allowed_actions"]:
            raise SemanticError(
                "emergency receipt requires emergency_rebalance action"
            )

    registry[data["receipt_id"]] = data


CANONICAL_INTEROPERABILITY_STAGES = {
    "origin", "trace", "authorization", "execution", "audit", "royalty"
}
CANONICAL_INTEROPERABILITY_SEQUENCE = {
    ("origin", "trace"),
    ("trace", "authorization"),
    ("authorization", "execution"),
    ("execution", "audit"),
    ("audit", "royalty"),
}


def infer_operation_type(record: dict[str, Any]) -> str | None:
    if "transition_id" in record:
        return "phase_transition"
    if "transformation_id" in record:
        return "residual_transformation"
    if "receipt_id" in record and "federation_id" in record:
        return "federated_rebalancing"
    return None


def local_context(record: dict[str, Any], operation_type: str) -> tuple[str, str]:
    if operation_type in {"phase_transition", "residual_transformation"}:
        return "cycle", record["cycle_id"]
    if operation_type == "federated_rebalancing":
        return "federation_epoch", record["epoch_id"]
    raise SemanticError(f"unsupported operation_type: {operation_type}")


def validate_interoperability_profile(
    data: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> None:
    stages = data["required_stages"]
    if set(stages) != CANONICAL_INTEROPERABILITY_STAGES or len(stages) != len(set(stages)):
        raise SemanticError(
            "required_stages must contain origin, trace, authorization, execution, audit, and royalty exactly once"
        )

    bound_stages = [item["stage"] for item in data["stage_bindings"]]
    if set(bound_stages) != CANONICAL_INTEROPERABILITY_STAGES or len(bound_stages) != len(set(bound_stages)):
        raise SemanticError("stage_bindings must bind every required stage exactly once")

    sequence = {
        (item["predecessor"], item["successor"])
        for item in data["sequence_constraints"]
    }
    if sequence != CANONICAL_INTEROPERABILITY_SEQUENCE:
        missing = sorted(CANONICAL_INTEROPERABILITY_SEQUENCE - sequence)
        extra = sorted(sequence - CANONICAL_INTEROPERABILITY_SEQUENCE)
        raise SemanticError(
            f"sequence_constraints must match the canonical Origin-to-Royalty order; missing={missing}, extra={extra}"
        )

    registry[data["profile_id"]] = data


def validate_circulation_operation_binding(
    data: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> None:
    profile = resolve_record(registry, data["profile_ref"], "profile_ref")
    if profile["status"] != "active":
        raise SemanticError("operation binding requires an active interoperability profile")

    local = resolve_record(registry, data["local_record_ref"], "local_record_ref")
    inferred = infer_operation_type(local)
    if inferred != data["operation_type"]:
        raise SemanticError(
            f"operation_type must be '{inferred}' for the referenced local record"
        )

    expected_context_type, expected_context_id = local_context(local, inferred)
    if data["context"]["context_type"] != expected_context_type:
        raise SemanticError(f"context_type must be '{expected_context_type}'")
    if data["context"]["context_id"] != expected_context_id:
        raise SemanticError("context_id must match the referenced local record")

    local_auth = local.get("authorization", {})
    local_decision = local_auth.get("decision")
    if local_decision and data["authorization"]["decision"] != local_decision:
        raise SemanticError("authorization decision must match the local operation")
    local_auth_ref = local_auth.get("authorization_ref")
    if local_auth_ref and data["authorization"]["receipt_ref"] != local_auth_ref:
        raise SemanticError("authorization receipt_ref must match the local operation")

    result_status = local.get("result", {}).get("status")
    if result_status in {"applied", "completed", "partial", "stabilized"}:
        if data["authorization"]["decision"] != "authorized":
            raise SemanticError("completed or applied operation requires authorized binding")
        if not data["authorization"]["scope_match"]:
            raise SemanticError("completed or applied operation requires scope_match=true")

    registry[data["binding_id"]] = data


def validate_circulation_execution_evidence(
    data: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> None:
    profile = resolve_record(registry, data["profile_ref"], "profile_ref")
    binding = resolve_record(registry, data["binding_ref"], "binding_ref")
    if binding["profile_ref"] != data["profile_ref"]:
        raise SemanticError("profile_ref must match the operation binding")
    if profile["status"] != "active":
        raise SemanticError("execution evidence requires an active profile")
    if data["context"] != binding["context"]:
        raise SemanticError("execution context must match the operation binding")
    if data["observed_operation_type"] != binding["operation_type"]:
        raise SemanticError("observed_operation_type must match the operation binding")

    status = data["execution_status"]
    if status in {"completed", "partial"}:
        if not data["authorization_match"]:
            raise SemanticError("completed or partial execution requires authorization_match=true")
        if binding["authorization"]["decision"] != "authorized":
            raise SemanticError("completed or partial execution requires an authorized binding")
        if "completed_at" not in data:
            raise SemanticError("completed or partial execution requires completed_at")
        if not data["outcome_refs"]:
            raise SemanticError("completed or partial execution requires outcome_refs")
    if "completed_at" in data and parse_dt(data["completed_at"]) < parse_dt(data["started_at"]):
        raise SemanticError("completed_at cannot be earlier than started_at")

    registry[data["execution_evidence_id"]] = data


def validate_circulation_audit_record(
    data: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> None:
    binding = resolve_record(registry, data["binding_ref"], "binding_ref")
    execution = resolve_record(
        registry, data["execution_evidence_ref"], "execution_evidence_ref"
    )
    if binding["profile_ref"] != data["profile_ref"]:
        raise SemanticError("profile_ref must match the operation binding")
    if execution["profile_ref"] != data["profile_ref"]:
        raise SemanticError("profile_ref must match execution evidence")
    if execution["binding_ref"] != data["binding_ref"]:
        raise SemanticError("execution evidence must reference the same binding")

    checks = data["checks"]
    all_checks = all(bool(value) for value in checks.values())
    findings = data["unresolved_findings"]
    decision = data["decision"]

    if decision == "pass":
        if not all_checks:
            raise SemanticError("pass audit requires every check to be true")
        if findings:
            raise SemanticError("pass audit cannot contain unresolved findings")
        if execution["execution_status"] not in {"completed", "partial"}:
            raise SemanticError("pass audit requires completed or partial execution")
    elif decision == "fail":
        if all_checks and not findings:
            raise SemanticError("fail audit requires a failed check or unresolved finding")
        if checks["royalty_eligible"]:
            raise SemanticError("failed audit cannot be royalty_eligible")
    else:
        if not findings:
            raise SemanticError("human review audit requires an unresolved finding")
        if checks["royalty_eligible"]:
            raise SemanticError("human review audit cannot be royalty_eligible")

    registry[data["audit_id"]] = data


def validate_circulation_royalty_settlement(
    data: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> None:
    binding = resolve_record(registry, data["binding_ref"], "binding_ref")
    audit = resolve_record(registry, data["audit_ref"], "audit_ref")
    if binding["profile_ref"] != data["profile_ref"]:
        raise SemanticError("profile_ref must match the operation binding")
    if audit["profile_ref"] != data["profile_ref"]:
        raise SemanticError("profile_ref must match the audit")
    if audit["binding_ref"] != data["binding_ref"]:
        raise SemanticError("audit_ref must audit the same operation binding")
    if data["context"] != binding["context"]:
        raise SemanticError("settlement context must match the operation binding")

    status = data["settlement_status"]
    allocations = data["allocations"]
    gross = float(data["value"]["gross_amount"])
    share_total = sum(float(item["share_ratio"]) for item in allocations)
    amount_total = sum(float(item["amount"]) for item in allocations)

    if status in {"settled", "held"}:
        if not allocations:
            raise SemanticError(f"{status} settlement requires allocations")
        require_close(share_total, 1.0, "allocation share ratios")
        require_close(amount_total, gross, "allocation amounts")

    if status == "settled":
        if audit["decision"] != "pass" or not audit["checks"]["royalty_eligible"]:
            raise SemanticError("settled receipt requires a passing royalty-eligible audit")
        if data["unresolved_dispute_refs"]:
            raise SemanticError("settled receipt cannot contain unresolved disputes")
        if "settled_at" not in data or "ledger_ref" not in data:
            raise SemanticError("settled receipt requires settled_at and ledger_ref")
    elif status == "held":
        if not data["unresolved_dispute_refs"] and audit["decision"] == "pass":
            raise SemanticError("held receipt requires a dispute or non-passing audit")
        if "settled_at" in data:
            raise SemanticError("held receipt cannot include settled_at")
    else:
        if allocations:
            raise SemanticError("rejected receipt cannot include allocations")
        if "settled_at" in data:
            raise SemanticError("rejected receipt cannot include settled_at")

    if "value_attribution_ref" in data:
        attribution = resolve_record(
            registry, data["value_attribution_ref"], "value_attribution_ref"
        )
        if binding["operation_type"] != "residual_transformation":
            raise SemanticError("value_attribution_ref is only valid for residual transformation")
        if attribution.get("cycle_id") != binding["context"]["context_id"]:
            raise SemanticError("value attribution cycle must match the binding context")

    registry[data["settlement_id"]] = data


def validate_civilization_os_conformance(
    data: dict[str, Any], registry: dict[str, dict[str, Any]]
) -> None:
    profile = resolve_record(registry, data["profile_ref"], "profile_ref")
    binding = resolve_record(registry, data["binding_ref"], "binding_ref")
    execution = resolve_record(
        registry, data["execution_evidence_ref"], "execution_evidence_ref"
    )
    audit = resolve_record(registry, data["audit_ref"], "audit_ref")
    settlement = resolve_record(registry, data["settlement_ref"], "settlement_ref")

    if binding["profile_ref"] != data["profile_ref"] or profile["status"] != "active":
        raise SemanticError("conformance assessment requires the same active profile")
    if execution["binding_ref"] != data["binding_ref"]:
        raise SemanticError("execution_evidence_ref must use the same binding")
    if audit["binding_ref"] != data["binding_ref"] or audit["execution_evidence_ref"] != data["execution_evidence_ref"]:
        raise SemanticError("audit_ref must audit the same binding and execution")
    if settlement["binding_ref"] != data["binding_ref"] or settlement["audit_ref"] != data["audit_ref"]:
        raise SemanticError("settlement_ref must use the same binding and audit")

    stage_items = data["checked_stages"]
    stages = [item["stage"] for item in stage_items]
    if set(stages) != CANONICAL_INTEROPERABILITY_STAGES or len(stages) != len(set(stages)):
        raise SemanticError("checked_stages must contain every stage exactly once")
    by_stage = {item["stage"]: item for item in stage_items}
    expected_refs = {
        "origin": binding["origin_ref"],
        "trace": binding["trace_ref"],
        "authorization": binding["authorization"]["receipt_ref"],
        "execution": data["execution_evidence_ref"],
        "audit": data["audit_ref"],
        "royalty": data["settlement_ref"],
    }
    for stage, expected_ref in expected_refs.items():
        if by_stage[stage]["record_ref"] != expected_ref:
            raise SemanticError(f"{stage} record_ref does not match the bound chain")

    statuses = [item["status"] for item in stage_items]
    if data["overall_status"] == "conformant":
        if any(status != "conformant" for status in statuses):
            raise SemanticError("conformant assessment requires every stage to be conformant")
        if data["findings"]:
            raise SemanticError("conformant assessment cannot contain findings")
        if audit["decision"] != "pass" or settlement["settlement_status"] != "settled":
            raise SemanticError("conformant assessment requires passed audit and settled royalty")
    elif data["overall_status"] == "nonconformant":
        if all(status == "conformant" for status in statuses):
            raise SemanticError("nonconformant assessment requires a missing or invalid stage")
        if not data["findings"]:
            raise SemanticError("nonconformant assessment requires findings")
    else:
        if not data["findings"]:
            raise SemanticError("human review assessment requires findings")

    registry[data["conformance_id"]] = data

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
    "residual-observation-record": validate_residual_observation,
    "residual-classification-record": validate_residual_classification,
    "residual-recovery-assessment": validate_residual_recovery_assessment,
    "residual-transformation-receipt": validate_residual_transformation,
    "regenerated-value-attribution": (
        validate_regenerated_value_attribution
    ),
    "circulation-governor-delegation": validate_governor_delegation,
    "federated-balance-assessment": validate_federated_balance_assessment,
    "federated-rebalancing-plan": validate_federated_rebalancing_plan,
    "rebalancing-conflict-resolution": (
        validate_rebalancing_conflict_resolution
    ),
    "federated-rebalancing-receipt": (
        validate_federated_rebalancing_receipt
    ),
    "civilization-os-interoperability-profile": (
        validate_interoperability_profile
    ),
    "circulation-operation-binding": (
        validate_circulation_operation_binding
    ),
    "circulation-execution-evidence": (
        validate_circulation_execution_evidence
    ),
    "circulation-audit-record": validate_circulation_audit_record,
    "circulation-royalty-settlement-receipt": (
        validate_circulation_royalty_settlement
    ),
    "civilization-os-conformance-assessment": (
        validate_civilization_os_conformance
    ),
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
    print("=== Yin-Yang Five-Phase Circulation Protocol v0.5 Validation ===")
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
