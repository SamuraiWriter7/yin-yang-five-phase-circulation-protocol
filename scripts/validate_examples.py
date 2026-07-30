#!/usr/bin/env python3
"""Validate Yin-Yang Five-Phase Circulation Protocol examples."""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"

PHASES = {"wood", "fire", "earth", "metal", "water"}
EPSILON = 1e-6

SCHEMA_FILES = {
    "five-phase-state-record":
        SCHEMA_DIR / "five-phase-state-record.schema.json",
    "yin-yang-balance-assessment":
        SCHEMA_DIR / "yin-yang-balance-assessment.schema.json",
    "polarity-shift-receipt":
        SCHEMA_DIR / "polarity-shift-receipt.schema.json",
}


class SemanticError(ValueError):
    """Raised when an example is schema-valid but semantically invalid."""


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

    raise SemanticError(
        f"cannot infer schema kind from filename: {path.name}"
    )


def require_close(
    actual: float,
    expected: float,
    label: str,
) -> None:
    if not math.isclose(
        actual,
        expected,
        rel_tol=0.0,
        abs_tol=EPSILON,
    ):
        raise SemanticError(
            f"{label}: expected {expected:.6f}, got {actual:.6f}"
        )


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
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    phase_states = data["phase_states"]
    phases = [item["phase"] for item in phase_states]

    if set(phases) != PHASES or len(phases) != len(set(phases)):
        raise SemanticError(
            "phase_states must contain each of wood, fire, earth, "
            "metal, and water exactly once"
        )

    total_yin = sum(
        float(item["yin_pressure"])
        for item in phase_states
    )
    total_yang = sum(
        float(item["yang_pressure"])
        for item in phase_states
    )

    if total_yin <= 0 or total_yang <= 0:
        raise SemanticError(
            "total Yin and Yang pressure must both be greater than zero"
        )

    balance_index = total_yang / total_yin
    aggregate = data["aggregate"]

    require_close(
        float(aggregate["total_yin_pressure"]),
        total_yin,
        "aggregate.total_yin_pressure",
    )
    require_close(
        float(aggregate["total_yang_pressure"]),
        total_yang,
        "aggregate.total_yang_pressure",
    )
    require_close(
        float(aggregate["balance_index"]),
        balance_index,
        "aggregate.balance_index",
    )

    has_critical_risk = any(
        float(item["risk_level"]) >= 0.9
        for item in phase_states
    )

    calculated_status = expected_status(
        balance_index,
        has_critical_risk,
    )

    if data["status"] != calculated_status:
        raise SemanticError(
            f"status must be '{calculated_status}' "
            "for the recorded pressures and risks"
        )

    registry[data["record_id"]] = data


def validate_balance_assessment(
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    thresholds = data["thresholds"]
    minimum = float(thresholds["minimum_balance_index"])
    maximum = float(thresholds["maximum_balance_index"])

    if minimum >= maximum:
        raise SemanticError(
            "minimum_balance_index must be lower "
            "than maximum_balance_index"
        )

    observed = data["observed"]
    total_yin = float(observed["total_yin_pressure"])
    total_yang = float(observed["total_yang_pressure"])
    balance_index = total_yang / total_yin

    require_close(
        float(observed["balance_index"]),
        balance_index,
        "observed.balance_index",
    )

    phase_assessments = data["phase_assessments"]
    phases = [
        item["phase"]
        for item in phase_assessments
    ]

    if set(phases) != PHASES or len(phases) != len(set(phases)):
        raise SemanticError(
            "phase_assessments must contain each phase exactly once"
        )

    has_critical = any(
        item["condition"] == "high_risk"
        or item["severity"] == "critical"
        for item in phase_assessments
    )

    calculated_status = expected_status(
        balance_index,
        has_critical,
        minimum,
        maximum,
    )

    if data["overall_status"] != calculated_status:
        raise SemanticError(
            f"overall_status must be '{calculated_status}'"
        )

    state_ref = data["state_record_ref"]
    state = registry.get(state_ref)

    if state is None:
        raise SemanticError(
            "state_record_ref does not resolve to "
            f"a validated pass record: {state_ref}"
        )

    if state["cycle_id"] != data["cycle_id"]:
        raise SemanticError(
            "cycle_id must match the referenced state record"
        )

    state_aggregate = state["aggregate"]

    require_close(
        total_yin,
        float(state_aggregate["total_yin_pressure"]),
        "assessment/state total_yin_pressure",
    )
    require_close(
        total_yang,
        float(state_aggregate["total_yang_pressure"]),
        "assessment/state total_yang_pressure",
    )
    require_close(
        balance_index,
        float(state_aggregate["balance_index"]),
        "assessment/state balance_index",
    )

    registry[data["assessment_id"]] = data


def comparator_holds(
    observed: float,
    comparator: str,
    threshold: float,
) -> bool:
    return {
        "gt": observed > threshold,
        "gte": observed >= threshold,
        "lt": observed < threshold,
        "lte": observed <= threshold,
        "eq": math.isclose(
            observed,
            threshold,
            rel_tol=0.0,
            abs_tol=EPSILON,
        ),
    }[comparator]


def validate_polarity_shift(
    data: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> None:
    previous = data["previous_polarity"]
    new = data["new_polarity"]

    if previous == new:
        raise SemanticError(
            "previous_polarity and new_polarity must differ"
        )

    for trigger in data["triggers"]:
        observed = float(trigger["observed_value"])
        threshold = float(trigger["threshold"])

        if not comparator_holds(
            observed,
            trigger["comparator"],
            threshold,
        ):
            raise SemanticError(
                "trigger condition is not satisfied "
                f"for metric '{trigger['metric']}'"
            )

    action_types = {
        action["action_type"]
        for action in data["actions"]
    }

    yin_actions = {
        "reduce_load",
        "route_workload",
        "hold_resources",
        "activate_cooling",
        "throttle_growth",
        "quarantine_residual",
        "review_dormant_residual",
    }

    yang_actions = {
        "increase_load",
        "route_workload",
        "release_resources",
        "activate_recovery",
        "stimulate_growth",
    }

    required_family = (
        yin_actions
        if new == "yin"
        else yang_actions
    )

    if action_types.isdisjoint(required_family):
        raise SemanticError(
            f"a shift to {new} requires "
            "at least one compatible action"
        )

    authorization = data["authorization"]
    result_status = data["result"]["status"]

    if result_status in {"applied", "stabilized"}:
        if authorization["decision"] != "authorized":
            raise SemanticError(
                "applied or stabilized shifts "
                "require an authorized decision"
            )

        if "effective_at" not in data:
            raise SemanticError(
                "applied or stabilized shifts require effective_at"
            )

    state_ref = data["state_record_ref"]
    assessment_ref = data["assessment_ref"]

    state = registry.get(state_ref)
    assessment = registry.get(assessment_ref)

    if state is None:
        raise SemanticError(
            f"state_record_ref does not resolve: {state_ref}"
        )

    if assessment is None:
        raise SemanticError(
            f"assessment_ref does not resolve: {assessment_ref}"
        )

    if (
        state["cycle_id"] != data["cycle_id"]
        or assessment["cycle_id"] != data["cycle_id"]
    ):
        raise SemanticError(
            "cycle_id must match both referenced records"
        )

    if assessment["state_record_ref"] != state_ref:
        raise SemanticError(
            "assessment_ref must assess "
            "the referenced state record"
        )

    matching_phase = next(
        item
        for item in state["phase_states"]
        if item["phase"] == data["phase"]
    )

    if matching_phase["polarity"] != previous:
        raise SemanticError(
            "previous_polarity must match "
            "the referenced phase state"
        )

    registry[data["shift_id"]] = data


SEMANTIC_VALIDATORS: dict[
    str,
    Callable[
        [dict[str, Any], dict[str, dict[str, Any]]],
        None,
    ],
] = {
    "five-phase-state-record":
        validate_five_phase_state,
    "yin-yang-balance-assessment":
        validate_balance_assessment,
    "polarity-shift-receipt":
        validate_polarity_shift,
}


def schema_errors(
    validator: Draft202012Validator,
    data: dict[str, Any],
) -> list[str]:
    messages: list[str] = []

    errors = sorted(
        validator.iter_errors(data),
        key=lambda item: list(item.absolute_path),
    )

    for error in errors:
        location = ".".join(
            str(part)
            for part in error.absolute_path
        ) or "<root>"

        messages.append(
            f"{location}: {error.message}"
        )

    return messages


def validate_pass_examples(
    validators: dict[str, Draft202012Validator],
) -> tuple[bool, dict[str, dict[str, Any]]]:
    registry: dict[str, dict[str, Any]] = {}
    ok = True

    for kind in SCHEMA_FILES:
        paths = sorted(
            PASS_DIR.glob(f"{kind}.*.yaml")
        )

        for path in paths:
            print(
                f"\n[validate-pass] "
                f"{path.relative_to(ROOT)}"
            )

            data = load_yaml(path)
            errors = schema_errors(
                validators[kind],
                data,
            )

            if errors:
                ok = False
                print("[schema-error]")

                for message in errors:
                    print(f"  - {message}")

                continue

            print("[schema-ok]")

            try:
                SEMANTIC_VALIDATORS[kind](
                    data,
                    registry,
                )
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

        print(
            f"\n[validate-fail] "
            f"{path.relative_to(ROOT)}"
        )

        data = load_yaml(path)
        errors = schema_errors(
            validators[kind],
            data,
        )

        if errors:
            print("[expected-schema-failure]")

            for message in errors:
                print(f"  - {message}")

            continue

        isolated_registry = dict(pass_registry)

        try:
            SEMANTIC_VALIDATORS[kind](
                data,
                isolated_registry,
            )
        except SemanticError as exc:
            print("[expected-semantic-failure]")
            print(f"  - {exc}")
        else:
            ok = False
            print("[unexpected-pass]")
            print(
                "  - fail example passed both "
                "schema and semantic validation"
            )

    return ok


def main() -> int:
    print(
        "=== Yin-Yang Five-Phase Circulation "
        "Protocol v0.1 Validation ==="
    )

    validators: dict[
        str,
        Draft202012Validator,
    ] = {}

    for kind, schema_path in SCHEMA_FILES.items():
        schema = load_schema(schema_path)
        Draft202012Validator.check_schema(schema)

        validators[kind] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

        print(
            f"schema [{kind}]: "
            f"{schema_path.relative_to(ROOT)}"
        )

    pass_ok, registry = validate_pass_examples(
        validators
    )

    fail_ok = validate_fail_examples(
        validators,
        registry,
    )

    if pass_ok and fail_ok:
        print("\nValidation succeeded.")
        return 0

    print("\nValidation failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
