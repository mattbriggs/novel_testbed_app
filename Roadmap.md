# Novel Testbed — Roadmap

This document tracks the current state of the system and the planned
evolution of the codebase. Items are organized by phase. Each phase
builds on a stable, fully-tested foundation.

---

## Current State (v1.0 — March 2026)

The system is a four-stage narrative compiler with a clean, testable pipeline:

```
segment → parse → infer → assess
```

### What works

| Feature | Status |
|---------|--------|
| Deterministic Markdown segmentation | Done |
| LLM-backed Markdown segmentation (`--llm`) | Done (fixed) |
| CommonMark parser (chapters + modules) | Done |
| Blank contract generation (YAML) | Done |
| LLM contract inference (OpenAI) | Done |
| Contract YAML serialization / loading | Done |
| Assessment rules (PASS / WARN / FAIL) | Done |
| JSON report output | Done |
| Source provenance / SHA-256 fingerprinting | Done |
| CLI: segment, parse, infer, assess | Done |
| Unit tests: 97 passing | Done |
| Integration test: full pipeline | Done |

### Design patterns in use

| Pattern | Where |
|---------|-------|
| Strategy | `NovelParser`, `ModuleSegmenter` / `LLMSegmenter` |
| Template Method | `ContractInferencer` (abstract base) |
| Protocol | `Rule` (structural typing for assessment rules) |
| Dependency Injection | `OpenAIContractInferencer(client=...)`, `LLMSegmenter(client=...)` |
| Chain of Responsibility | State chaining in `OpenAIContractInferencer.infer()` |

---

## Phase 2 — Richer Assessment Engine

**Goal:** Make the rule system expressive enough to detect common narrative
failure modes automatically.

### Planned rules

| Rule | Description |
|------|-------------|
| `FlatArcRule` | Detect runs of N modules with no state change |
| `ThreatPeakRule` | Warn if threat never reaches a configurable threshold |
| `AgencyCollapseRule` | Fail if protagonist agency drops to zero and never recovers |
| `GenreShiftRule` | Flag unexplained mid-novel genre changes |
| `FantasyAlignmentRule` | Validate that `dominant_fantasy_id` is consistent across a chapter |
| `RedundantModuleRule` | Warn if two adjacent modules have identical `expected_changes` |

### Planned improvements

- Configurable rule sets via YAML config file
- Rule severity overrides (downgrade FAIL → WARN for a specific rule)
- `assess --rules path/to/rules.yaml` CLI flag

---

## Phase 3 — Reporting and Visualization

**Goal:** Make output human-readable and actionable for a working author.

### Planned outputs

- **Markdown report** — human-readable narrative summary alongside JSON
- **Pressure curve** — ASCII or Mermaid chart of `threat_level` across modules
- **Dead zone map** — highlight inert modules inline in the source Markdown
- **Chapter summary** — aggregate severity per chapter

### Planned CLI additions

```bash
novel-testbed report contract.yaml -o report.md
novel-testbed pressure-curve contract.yaml
```

---

## Phase 4 — Alternative Backends

**Goal:** Allow non-OpenAI inference and rule-based NLP analysis.

### Planned

| Backend | Description |
|---------|-------------|
| `AnthropicContractInferencer` | Claude-based inference via the Anthropic SDK |
| `NLPContractInferencer` | Rule-based NLP using spaCy (no API key required) |
| `HybridContractInferencer` | NLP priors + LLM refinement |
| Local model support | Any Ollama-compatible local LLM |

This requires no changes to the assessment layer — new inferencers implement
`ContractInferencer.infer()` and slot in transparently.

---

## Phase 5 — Multi-Chapter and Multi-File Support

**Goal:** Support full novel files spanning many chapters and sub-files.

### Planned

- `novel-testbed segment-dir novels/ -o annotated/` — batch segmentation
- Multi-file contract assembly
- Cross-chapter state continuity tracking
- Chapter-level contracts (aggregated from module contracts)
- Revision detection: re-assess only changed modules (via SHA-256 diff)

---

## Phase 6 — Editor Integration

**Goal:** Bring feedback directly into the writing environment.

### Planned

- **VS Code extension** — inline WARN/FAIL annotations on module headings
- **Obsidian plugin** — live contract sidebar for vault-based writing
- **Scrivener export adapter** — parse Scrivener MMD exports as input
- **Web UI** — single-page contract editor with live assessment

---

## Phase 7 — Contract Schema Evolution

**Goal:** Enrich the contract model to support more nuanced narrative analysis.

### Planned fields

```yaml
# New ReaderState fields
suspicion_level: 0..1
captivity_pressure: 0..1
moral_distortion: 0..1
trust_erosion: 0..1
attachment_level: 0..1

# New ModuleContract fields
pov_character: str
narrative_distance: close | medium | distant
structural_role: setup | escalation | reversal | resolution
```

### Fantasy ID registry

- Formalize `dominant_fantasy_id` as a lookup against a registry YAML
- Validate IDs at assessment time
- Support user-defined fantasy registries

---

## Phase 8 — Calibration and Feedback Loop

**Goal:** Allow the system to learn from author corrections.

### Planned

- `infer --review` mode: show inference side-by-side with blank contract for
  author confirmation
- Contract diff: compare two contract versions to surface revision effects
- Calibration dataset: store author-corrected contracts to fine-tune prompts
- Confidence threshold enforcement: reject low-confidence inferences
  (< configurable value) and request manual fill

---

## Known Limitations (v1.0)

| Limitation | Notes |
|------------|-------|
| OpenAI only for LLM paths | Phase 4 adds alternatives |
| No multi-file support | Phase 5 |
| Assessment rules are minimal | Phase 2 |
| No human-readable report output | Phase 3 |
| `ReaderState` fields are fixed | Phase 7 adds extensibility |
| No revision / drift detection | Phase 5 |
| Module IDs are positional (`M001`) | Will become content-hashed in Phase 5 |

---

## Versioning Policy

- `v1.x` — current stable line; bug fixes and test improvements only
- `v2.0` — Phase 2 rule engine; minor breaking changes to rule API
- `v3.0` — Phase 4 multi-backend; breaking changes to inferencer interface

---

*This document is updated at each release milestone.*
