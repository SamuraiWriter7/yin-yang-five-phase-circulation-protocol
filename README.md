# Yin-Yang Five-Phase Circulation Protocol

A protocol for stabilizing distributed AI infrastructure through dynamic Yin-Yang regulation, Five-Phase circulation, residual recovery, federated rebalancing, and auditable value regeneration.

## Status

* Repository release: `0.5.0`
* Specification maturity: experimental
* Schema dialect: JSON Schema Draft 2020-12
* Example format: YAML
* Reference validator: Python
* Initial specification series: complete through v0.5

## Purpose

Distributed AI infrastructure cannot remain stable through expansion, computation, and resource consumption alone.

It must also be able to:

* expand and contract;
* execute and rest;
* release and retain;
* generate and recover;
* circulate and regulate;
* preserve causal history;
* authorize intervention;
* audit outcomes;
* return value to its origins.

The Yin-Yang Five-Phase Circulation Protocol turns those requirements into auditable records and semantic validation rules.

It models distributed infrastructure as a dynamic circulation system rather than a collection of independent compute nodes.

```text
Yin-Yang
  controls intensity, direction, expansion, and contraction

Five Phases
  transform growth, computation, state, verification, and flow

Residual-to-Resource
  returns recoverable loss to productive circulation

Federation
  rebalances local scarcity and surplus across members

Civilization OS interoperability
  binds Origin, Trace, Authorization, Execution, Audit, and Royalty
```

## Core design principle

> Five Phases determine how resources and value change form. Yin and Yang determine whether each phase expands, contracts, releases, retains, executes, or rests.

The goal is not endless motion or permanent equilibrium.

The goal is a system that can remain within a safe operating range while preserving the reason, authority, evidence, and value attribution behind every adjustment.

## Conceptual model

### Yin and Yang

Yin and Yang are operating polarities within every phase. They are not additional phases.

* **Yang** represents outward activity, execution, release, growth, activation, and circulation.
* **Yin** represents inward activity, retention, cooling, review, rest, preparation, and recovery.

A stable system may lean toward Yang during growth or toward Yin during recovery. Stability therefore means controlled oscillation, not static equality.

### Five Phases

| Phase | Infrastructure role                                | Typical Yang mode                             | Typical Yin mode                           |
| ----- | -------------------------------------------------- | --------------------------------------------- | ------------------------------------------ |
| Wood  | Growth, node activation, capability formation      | Expansion, onboarding, activation             | Preparation, incubation, dormancy          |
| Fire  | Compute, inference, execution, heat generation     | High activity, task execution, value creation | Throttling, cooling, low-power operation   |
| Earth | State, storage, Trace retention, grounding         | Commitment, accumulation, stabilization       | Compression, reclassification, forgetting  |
| Metal | Verification, authorization, valuation, settlement | Decision, enforcement, pruning, allocation    | Review, holdback, dispute, refinement      |
| Water | Cooling, routing, liquidity, resource flow         | Distribution, movement, release               | Retention, reserve, flow control, recovery |

### Generating cycle

The canonical generating cycle moves resources and value toward the next productive form.

```text
Wood → Fire → Earth → Metal → Water → Wood
```

* Wood generates Fire: new nodes and capabilities enable execution.
* Fire generates Earth: execution produces state, evidence, and residuals.
* Earth generates Metal: retained evidence becomes verifiable value and rules.
* Metal generates Water: verified value becomes authorized flow and allocation.
* Water generates Wood: circulating resources enable renewed growth.

### Controlling cycle

The canonical controlling cycle prevents unbounded expansion and local failure.

```text
Wood → Earth
Earth → Water
Water → Fire
Fire → Metal
Metal → Wood
```

* Wood controls Earth by consuming, renewing, and pruning stored state.
* Earth controls Water by retaining, bounding, and securing uncontrolled flow.
* Water controls Fire through cooling, routing, and load redistribution.
* Fire controls Metal by exposing whether rules and valuations survive real execution.
* Metal controls Wood through authorization, evaluation, and pruning.

### Residual-to-Resource

A residual is not assumed to be waste. It is a by-product whose next valid use has not yet been established.

```text
Execution
  ↓
Residual observation
  ↓
Classification
  ├─ Recoverable → assessment → authorized transformation
  ├─ Dormant     → vault → periodic review
  └─ Hazardous   → quarantine → audit, sanitization, or purge
```

The protocol distinguishes:

* `recoverable`: safe and potentially valuable in another process;
* `dormant`: not currently usable but eligible for later review;
* `hazardous`: unsafe, corrupting, malicious, or otherwise unsuitable for active circulation.

Circulation does not mean that everything must be reused. It means that every residual is evaluated before disposal, storage, quarantine, or transformation.

## Specification architecture

The repository release is `0.5.0`, but record families retain the schema version in which they were introduced.

| Layer                            | Schema version | Primary responsibility                                                           |
| -------------------------------- | -------------- | -------------------------------------------------------------------------------- |
| Yin-Yang state and polarity      | `0.1.0`        | Observe phase state, assess balance, record polarity shifts                      |
| Five-Phase transitions           | `0.2.0`        | Enforce generating and controlling paths, cooldown, and transition authorization |
| Residual-to-Resource             | `0.3.0`        | Observe, classify, assess, transform, and attribute regenerated value            |
| Federated rebalancing            | `0.4.0`        | Coordinate multiple nodes and regions under delegated authority                  |
| Civilization OS interoperability | `0.5.0`        | Bind Origin-to-Royalty evidence and perform end-to-end conformance checks        |

Existing schema versions are intentionally preserved. A repository update does not silently rewrite earlier record contracts.

## Record catalog

### v0.1 — Yin-Yang state and polarity

#### `Five-Phase State Record`

Records the current Yin and Yang pressures, activity, utilization, and risk for Wood, Fire, Earth, Metal, and Water.

#### `Yin-Yang Balance Assessment`

Evaluates phase-level and cycle-wide stability against configurable balance and critical-risk thresholds.

#### `Polarity Shift Receipt`

Records an authorized Yin-to-Yang or Yang-to-Yin shift, including triggers, actions, authority, timing, and result.

### v0.2 — Five-Phase transition rules

#### `Five-Phase Transition Policy`

Defines canonical generating and controlling edges, blocked paths, human-review paths, cooldown requirements, and emergency-bypass policy.

#### `Phase Transition Evaluation`

Evaluates a proposed transition against the canonical cycles, explicit restrictions, polarity context, timing, and cooldown rules.

#### `Phase Transition Receipt`

Records authorization and execution evidence for an evaluated Five-Phase transition.

### v0.3 — Residual-to-Resource integration

#### `Residual Observation Record`

Records where a residual originated, its type, quantity, unit, source phase, and evidence references.

#### `Residual Classification Record`

Assigns `recoverable`, `dormant`, or `hazardous` status with confidence, evidence, routing constraints, vault requirements, quarantine requirements, and review timing.

#### `Residual Recovery Assessment`

Calculates whether recovery is viable by evaluating converted utility, recovery efficiency, temporal fit, spatial fit, trust, collection cost, conversion cost, and risk cost.

#### `Residual Transformation Receipt`

Records an authorized residual transformation, including input value, output value, loss, unallocated value, route, execution status, and evidence.

#### `Regenerated Value Attribution`

Reconnects regenerated value to its originating records and beneficiaries while preventing share mismatch, amount mismatch, and duplicate accounting.

### v0.4 — Federated rebalancing

#### `Circulation Governor Delegation`

Delegates limited authority to a circulation governor by region, member, phase, action, capacity ratio, validity window, and emergency scope.

#### `Federated Balance Assessment`

Aggregates member states and identifies balanced operation, localized imbalance, or federation-wide instability.

#### `Federated Rebalancing Plan`

Defines proposed transfers of compute, cooling, storage, bandwidth, liquidity, workload, or related resources between federation members.

#### `Rebalancing Conflict Resolution`

Selects and rejects competing transfers while requiring complete, non-overlapping conflict resolution.

#### `Federated Rebalancing Receipt`

Records authorized transfers and rejects execution that exceeds delegation, executes rejected candidates, or bypasses unresolved conflicts.

### v0.5 — Civilization OS interoperability and conformance

#### `Civilization OS Interoperability Profile`

Defines the canonical evidence-chain order and external protocol bindings.

```text
Origin → Trace → Authorization → Execution → Audit → Royalty
```

#### `Circulation Operation Binding`

Binds a local phase transition, residual transformation, or federated rebalancing operation to external Origin, Trace, Authorization, actor, and Human Axis references.

#### `Circulation Execution Evidence`

Records what was actually executed and verifies that the observed operation matches the bound authorization and operation type.

#### `Circulation Audit Record`

Checks Origin resolution, Trace resolution, authorization consistency, execution consistency, phase-policy conformance, and royalty eligibility.

#### `Circulation Royalty Settlement Receipt`

Records allocation and settlement after a successful audit while enforcing share totals, amount totals, dispute status, and ledger references.

#### `Civilization OS Conformance Assessment`

Performs an end-to-end assessment across Origin, Trace, Authorization, Execution, Audit, and Royalty.

## End-to-end lifecycle

```text
1. Observe local Five-Phase state
        ↓
2. Assess Yin-Yang balance
        ↓
3. Shift polarity or evaluate a phase transition
        ↓
4. Execute an authorized local operation
        ↓
5. Observe and classify generated residuals
        ↓
6. Recover, vault, or quarantine residuals
        ↓
7. Rebalance across federation members when necessary
        ↓
8. Bind the operation to Origin, Trace, and Authorization
        ↓
9. Record Execution evidence
        ↓
10. Audit consistency and eligibility
        ↓
11. Attribute and settle regenerated value
        ↓
12. Assess end-to-end conformance
```

## Balance model

The default v0.1 cycle-wide balance index is:

```text
balance_index = total_yang_pressure / total_yin_pressure
```

Default interpretation:

| Balance index         | Status          |
| --------------------- | --------------- |
| `< 0.80`              | `yin_dominant`  |
| `0.80` through `1.20` | `balanced`      |
| `> 1.20`              | `yang_dominant` |

If any phase risk reaches or exceeds the configured critical-risk threshold, the cycle becomes `unstable` regardless of aggregate balance.

These defaults are conformance values for the initial protocol, not universal physical constants. Implementations may externalize alternative thresholds through policy while preserving record semantics.

## Residual value model

The reference validator uses the following conceptual calculation:

```text
Gross Adjusted Value
=
Converted Utility
× Recovery Efficiency
× Temporal Fit
× Spatial Fit
× Trust Factor
```

```text
Net Residual Value
=
Gross Adjusted Value
− Collection Cost
− Conversion Cost
− Risk Cost
```

A technically recoverable residual may still be classified as `not_viable` when its net value does not satisfy policy.

Transformation accounting must preserve:

```text
Input Equivalent Value
=
Output Equivalent Value
+ Conversion Loss
+ Unallocated Value
```

Regenerated-value attribution must preserve:

```text
sum(contribution weights) = 1.0
sum(allocation share ratios) = 1.0
sum(allocation amounts) = regenerated value
```

A unique value-accounting key prevents the same regenerated value from being counted repeatedly.

## Federated authority model

Federation is not equivalent to central control.

A circulation governor receives only the authority explicitly delegated to it.

A delegation constrains:

* valid members and regions;
* permitted phases;
* allowed actions;
* maximum transferable capacity;
* validity period;
* emergency authority.

Emergency authority must be explicit. A general authorization does not imply permission to perform emergency rebalancing.

A rebalancing plan MUST NOT:

* transfer more than a source member can safely provide;
* exceed the delegated maximum transfer ratio;
* use a member outside the delegated scope;
* use a phase or action outside the delegated scope;
* execute a rejected conflict candidate;
* execute while required conflict resolution remains incomplete.

## Civilization OS evidence chain

v0.5 uses stable references rather than embedding external protocol records.

```text
Origin
  establishes where the operation or value began

Trace
  preserves causal continuity

Authorization
  proves the operation was permitted before execution

Execution
  records what actually occurred

Audit
  checks consistency, policy conformance, and eligibility

Royalty
  returns value to eligible origins and contributors
```

A conformant chain MUST preserve this order.

The protocol rejects structures such as:

* execution followed by retrospective authorization;
* completed execution with authorization mismatch;
* audit pass when any required check is false;
* royalty settlement after audit failure;
* settlement with unresolved disputes;
* a conformance claim with a missing Trace stage;
* substitution of an unrelated Origin or local operation reference.

## Normative requirements

An implementation conforming to the applicable layers MUST:

* use the schema version required by each record family;
* record Wood, Fire, Earth, Metal, and Water exactly once where a complete phase set is required;
* preserve cross-record identifiers and context identifiers;
* calculate aggregate values from the referenced underlying records;
* reject same-polarity shifts;
* reject noncanonical or explicitly blocked transition paths unless an applicable policy permits review or emergency handling;
* enforce cooldown policy before transition execution;
* require authorization for applied or completed operations;
* prevent non-recoverable residuals from entering active transformation;
* vault Dormant residuals with a review time;
* quarantine Hazardous residuals and prevent active routing;
* preserve residual value accounting across transformation;
* prevent duplicate regenerated-value accounting;
* constrain federation actions to delegated authority;
* resolve transfer conflicts before execution;
* preserve the canonical Origin-to-Royalty evidence sequence;
* require audit success before settled royalty;
* reject settlement with unresolved disputes;
* mark end-to-end conformance as successful only when every required stage is conformant.

An implementation SHOULD:

* preserve evidence references for every classification, decision, transition, transformation, transfer, audit, and settlement;
* use confidence and review timing for classifications that may change;
* retain minimum audit evidence for Hazardous material even when active content is sanitized or purged;
* avoid maximizing circulation speed at the expense of safety, trust, or recovery value;
* keep local autonomy separate from federation emergency authority;
* use external registries or cryptographic proofs where stronger identity and integrity guarantees are required.

## Repository layout

```text
yin-yang-five-phase-circulation-protocol/
├── .github/
│   └── workflows/
│       └── validate.yml
├── examples/
│   ├── fail/
│   └── pass/
├── schemas/
│   ├── five-phase-state-record.schema.json
│   ├── yin-yang-balance-assessment.schema.json
│   ├── polarity-shift-receipt.schema.json
│   ├── five-phase-transition-policy.schema.json
│   ├── phase-transition-evaluation.schema.json
│   ├── phase-transition-receipt.schema.json
│   ├── residual-observation-record.schema.json
│   ├── residual-classification-record.schema.json
│   ├── residual-recovery-assessment.schema.json
│   ├── residual-transformation-receipt.schema.json
│   ├── regenerated-value-attribution.schema.json
│   ├── circulation-governor-delegation.schema.json
│   ├── federated-balance-assessment.schema.json
│   ├── federated-rebalancing-plan.schema.json
│   ├── rebalancing-conflict-resolution.schema.json
│   ├── federated-rebalancing-receipt.schema.json
│   ├── civilization-os-interoperability-profile.schema.json
│   ├── circulation-operation-binding.schema.json
│   ├── circulation-execution-evidence.schema.json
│   ├── circulation-audit-record.schema.json
│   ├── circulation-royalty-settlement-receipt.schema.json
│   └── civilization-os-conformance-assessment.schema.json
├── scripts/
│   └── validate_examples.py
├── CHANGELOG.md
├── README.md
└── requirements.txt
```

## Validation

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the validator:

```bash
python scripts/validate_examples.py
```

The validator checks:

* JSON Schema Draft 2020-12 validity;
* schema conformance for pass and fail examples;
* semantic rules that cannot be expressed cleanly in JSON Schema alone;
* aggregate calculations;
* canonical generating and controlling cycles;
* cooldown and emergency-bypass logic;
* cross-record references;
* residual classification and value calculations;
* federation delegation and transfer limits;
* conflict-resolution completeness;
* Origin-to-Royalty evidence-chain consistency;
* expected failure behavior.

A successful run ends with:

```text
Validation succeeded.
```

Fail examples are successful tests when they are rejected for the intended semantic or schema reason.

## Example conformance chain

```text
five-phase-state-fire-overheated-001
  ↓
yin-yang-assessment-fire-overheat-001
  ↓
phase-transition-evaluation-water-fire-001
  ↓
phase-transition-water-fire-001
  ↓
residual-observation-thermal-001
  ↓
residual-classification-thermal-recoverable-001
  ↓
residual-recovery-assessment-thermal-001
  ↓
residual-transformation-thermal-001
  ↓
regenerated-value-attribution-thermal-001
  ↓
circulation-operation-binding-001
  ↓
circulation-execution-evidence-001
  ↓
circulation-audit-001
  ↓
circulation-royalty-settlement-001
  ↓
civilization-os-conformance-assessment-001
```

Implementations may use different identifiers, but the causal and authorization relationships must remain resolvable.

## Interoperability boundary

This repository defines record contracts and reference validation. It does not duplicate the complete schemas of external Civilization OS protocols.

External records are bound by stable references such as:

* Origin records;
* Trace records;
* action authorization receipts;
* Human Axis bindings;
* audit evidence;
* royalty allocation ledgers;
* dispute and settlement records.

The following remain implementation responsibilities unless another referenced protocol defines them:

* cryptographic signature verification;
* remote registry resolution;
* identity proofing;
* distributed consensus;
* token issuance;
* payment execution;
* hardware attestation;
* physical heat-transfer engineering;
* legal and regulatory compliance.

## Non-goals

This protocol does not claim to:

* create a perpetual-motion system;
* eliminate thermodynamic loss;
* guarantee that every residual has positive recovery value;
* replace physical infrastructure engineering;
* prescribe one token or blockchain architecture;
* centralize all federation decisions under one governor;
* treat Yin-Yang or Five-Phase terminology as a substitute for measurable system state;
* prove external records cryptographically without an external verifier.

The terminology is used as a system-control abstraction. Conformance depends on measurable fields, explicit policies, record references, and validator rules.

## Release boundary

v0.5 closes the initial specification series.

The repository now covers:

```text
State
→ Balance
→ Polarity
→ Transition
→ Residual recovery
→ Federation
→ Origin-to-Royalty conformance
```

Further expansion should favor one of the following paths:

1. a `1.0.0` stabilization and conformance release;
2. a separate reference-implementation repository;
3. a dedicated protocol for runtime scheduling and physical resource adapters;
4. integration profiles maintained in separate repositories.

This prevents the core record family from expanding without a clear architectural boundary.

## Design statement

> Infrastructure is not sustained by computation alone. It is sustained by the ability to observe imbalance, regulate intensity, transform state, recover residuals, share capacity, preserve causality, authorize action, audit results, and return value to its sources.

Yin regulates Yang. The Five Phases circulate resources. Residuals become new inputs only after evaluation. Federation shares capacity without erasing local authority. Trace and Audit keep circulation from becoming unaccountable, and Royalty closes the value loop.
