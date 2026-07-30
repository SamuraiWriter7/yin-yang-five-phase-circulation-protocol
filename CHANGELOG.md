Changelog

All notable changes to the Yin-Yang Five-Phase Circulation Protocol are documented in this file.

The format is based on Keep a Changelog. Specification releases use semantic versioning at the repository level, while record families retain the schema version in which they were introduced.

[Unreleased]

Planned

Stabilization review for a possible 1.0.0 conformance release.

Stronger schema documentation and machine-readable conformance profiles.

Optional reference adapters for external Origin, Trace, Authorization, Audit, and Royalty protocols.

Expanded multi-cycle and multi-federation test scenarios.

Reference implementation guidance separated from the core record contracts.

[0.5.0] - 2026-07-30

Added

Civilization OS Interoperability Profile with the canonical evidence-chain order:

Origin → Trace → Authorization → Execution → Audit → Royalty

Circulation Operation Binding for connecting local operations to external Origin, Trace, Authorization, actor, and Human Axis references.

Binding support for:

phase transitions;

residual transformations;

federated rebalancing.

Circulation Execution Evidence for recording the observed operation, execution state, resource use, Trace references, and authorization consistency.

Circulation Audit Record with checks for:

Origin resolution;

Trace resolution;

authorization match;

execution consistency;

phase-policy conformance;

royalty eligibility.

Circulation Royalty Settlement Receipt with validation for:

audit decision;

royalty eligibility;

allocation shares;

allocation amounts;

unresolved disputes;

ledger references;

settlement state.

Civilization OS Conformance Assessment for end-to-end validation of Origin, Trace, Authorization, Execution, Audit, and Royalty.

Pass examples for all six v0.5 record types.

Fail examples covering:

noncanonical stage order;

authorization mismatch;

unauthorized completed execution;

false audit pass;

settlement with unresolved disputes;

conformance with missing Trace.

Reference-validator integration for all v0.1 through v0.5 record families.

Changed

Updated the repository validation banner and schema registry for v0.5.

Extended semantic validation to resolve local v0.1–v0.4 operations before evaluating v0.5 bindings and evidence.

Added cross-record checks that prevent an unrelated local operation, authorization, audit, or settlement from being substituted into a conformance chain.

Documented the initial specification-series completion boundary.

Security

Completed local operations cannot be bound to a denied authorization.

Completed or partial execution requires a positive authorization match.

An audit cannot pass when any required check is false or blocking findings remain unresolved.

Royalty cannot be settled after a failed or ineligible audit.

Settled receipts cannot contain unresolved disputes.

End-to-end conformance cannot be declared when a required stage is missing or nonconformant.

Compatibility

Existing v0.1–v0.4 schemas retain their original schema versions.

External protocol records are referenced rather than embedded.

Cryptographic verification and remote registry resolution remain implementation responsibilities.

Design boundary

v0.5 closes the initial specification series.

Future major expansion should move toward a 1.0.0 stabilization release, a reference-implementation repository, or separate integration profiles rather than continuously enlarging the same core record family.

[0.4.0] - 2026-07-30

Added

Circulation Governor Delegation for scoped federation authority.

Delegation constraints for:

regions;

members;

phases;

allowed actions;

maximum transfer ratios;

validity windows;

emergency authority.

Federated Balance Assessment for aggregating multiple member states.

Federation statuses:

balanced;

localized_imbalance;

federation_unstable.

Federated Rebalancing Plan for proposed resource transfers between members.

Transfer support for compute, cooling, storage, bandwidth, liquidity, workload, and related resource categories.

Rebalancing Conflict Resolution for selecting and rejecting competing transfers.

Federated Rebalancing Receipt for recording authorized execution and post-rebalancing evidence.

Pass examples for delegated emergency rebalancing, localized imbalance, conflict resolution, and completed federation transfers.

Fail examples covering invalid delegation windows, duplicate members, delegation-limit violations, overlapping conflict results, and execution of rejected transfers.

Changed

Extended the protocol from single-cycle regulation to multi-member and multi-region circulation.

Added federation-level registry and semantic validation in dependency order.

Required selected and rejected conflict candidates to form a complete, disjoint partition of the competing transfer set.

Security

Governors cannot operate outside explicitly delegated members, regions, phases, actions, or time windows.

Transfer plans cannot exceed available source capacity or delegated transfer ratios.

Emergency rebalancing requires both emergency authority and an explicit emergency_rebalance action permission.

Receipts cannot execute rejected or unresolved transfer candidates.

Compatibility

v0.1, v0.2, and v0.3 schemas retain versions 0.1.0, 0.2.0, and 0.3.0 respectively.

Only the five federation record families use schema_version: "0.4.0".

Design boundary

v0.4 coordinates already modeled circulation resources; it does not define network transport, payment rails, or distributed consensus.

Federation authority remains delegated and bounded rather than implicitly centralized.

[0.3.0] - 2026-07-30

Added

Formal Residual-to-Resource integration.

Residual Observation Record for recording residual origin, type, quantity, unit, source phase, and evidence.

Residual Classification Record with tri-state classification:

recoverable;

dormant;

hazardous.

Confidence, evidence, review timing, candidate-target, vault, quarantine, and sanitization fields for residual classification.

Residual Recovery Assessment with adjusted-value and net-value calculation.

Recovery factors for:

converted utility;

recovery efficiency;

temporal fit;

spatial fit;

trust;

collection cost;

conversion cost;

risk cost.

Residual Transformation Receipt for authorized conversion, routing, value conservation, loss, and evidence.

Regenerated Value Attribution for reconnecting regenerated value to origins and beneficiaries.

Unique value-accounting keys for duplicate-accounting prevention.

Pass examples for thermal recovery, Dormant information, Hazardous information, viable assessment, completed transformation, and regenerated-value attribution.

Fail examples covering missing Dormant review, active routing of Hazardous material, recovery of non-recoverable material, incorrect net-value calculations, unauthorized completed transformation, and invalid allocation totals.

Changed

Extended the circulation lifecycle from state and transition control to resource metabolism.

Added dependency-ordered validation:

Observation
→ Classification
→ Assessment
→ Transformation
→ Attribution

Added cross-record Origin, classification, assessment, transformation, and attribution checks.

Security

Dormant residuals require a vault reference and review time.

Hazardous residuals require quarantine and cannot enter an active route.

Only Recoverable residuals may enter a recovery assessment.

Completed or partial transformations require authorization.

Regenerated-value allocation weights and amounts must reconcile exactly.

A unique accounting key prevents repeated recognition of the same regenerated value.

Compatibility

v0.1 and v0.2 record families retain schema versions 0.1.0 and 0.2.0.

Only the five Residual-to-Resource record families use schema_version: "0.3.0".

Design boundary

v0.3 evaluates and accounts for residual recovery but does not claim that every residual is reusable or economically viable.

Physical conversion engineering remains outside the schema contract.

[0.2.0] - 2026-07-30

Added

Five-Phase Transition Policy defining the canonical generating cycle:

Wood → Fire → Earth → Metal → Water → Wood

Canonical controlling cycle:

Wood → Earth
Earth → Water
Water → Fire
Fire → Metal
Metal → Wood

Explicit blocked-transition and human-review-transition lists.

Generating and controlling cooldown policies.

Emergency cooldown-bypass policy.

Phase Transition Evaluation for relation, timing, cooldown, emergency, restriction, and decision checks.

Phase Transition Receipt for recording authorization and transition execution.

Pass examples for:

Water-to-Wood generating transition;

Water-to-Fire controlling transition;

cooldown-based denial;

explicit blocked-path denial;

completed generating and controlling transition receipts.

Fail examples for malformed canonical cycles, blocked-path approval, cooldown bypass, and execution based on a denied evaluation.

A balanced Yin-Yang assessment example required by Water-to-Wood reference chains.

Changed

Upgraded the Five-Phase model from state description to an enforceable transition graph.

Added cross-record checks among state records, assessments, transition policies, evaluations, and receipts.

Required cooldown elapsed time and declared satisfaction to agree.

Security

Correct direction alone is insufficient; transitions must also satisfy timing and policy.

Explicitly blocked paths cannot be approved as ordinary transitions.

Applied or completed transitions require an approvable evaluation and authorization.

A transition receipt must match the evaluated source phase, target phase, relation, polarity, context, and policy.

Compatibility

v0.1 state, assessment, and polarity records retain schema_version: "0.1.0".

Only the three transition record families use schema_version: "0.2.0".

Design boundary

v0.2 defines logical phase transitions and control timing.

Residual classification, transformation, and value regeneration were reserved for v0.3.

[0.1.0] - 2026-07-30

Added

Initial Yin-Yang Five-Phase circulation model.

Canonical phases:

wood;

fire;

earth;

metal;

water.

Canonical polarities:

yin;

yang.

Five-Phase State Record for recording every phase exactly once.

Per-phase measurements for:

polarity;

Yin pressure;

Yang pressure;

activity level;

capacity utilization;

risk level.

Cycle aggregate fields for total Yin pressure, total Yang pressure, and balance index.

Yin-Yang Balance Assessment for phase-level and cycle-wide stability analysis.

Default balance thresholds:

below 0.80: yin_dominant;

0.80 through 1.20: balanced;

above 1.20: yang_dominant.

Critical-risk override for phase risk at or above 0.90.

Polarity Shift Receipt for auditable Yin-to-Yang and Yang-to-Yin changes.

Trigger, action, authorization, timing, and result fields for polarity shifts.

Pass examples for balanced operation, Fire overheat, balance assessment, and Fire Yang-to-Yin stabilization.

Fail examples for duplicate phases, incorrect status, and same-polarity shifts.

Python reference validator with JSON Schema, semantic, aggregate, trigger, and cross-record validation.

GitHub Actions workflow for automated validation.

Security

Every state record must contain each phase exactly once.

Recorded aggregate values must equal values calculated from phase states.

Applied or stabilized polarity shifts require prior authorization and an effective time.

Trigger conditions must be true rather than merely declared.

Shift actions must be compatible with the requested polarity direction.

Design boundary

v0.1 records state, assessment, and polarity shifts.

Generating and controlling transition relations were reserved for v0.2.

Residual recovery, federation, and Civilization OS interoperability were outside the initial release.
