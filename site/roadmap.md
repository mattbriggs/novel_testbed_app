# Roadmap

The Novel Testbed roadmap is maintained in the repository root:

[Roadmap.md](https://github.com/mattbriggs/novel_testbed_app/blob/main/Roadmap.md)

## Recent Changes

## 2026-03-07

**Cleanup pass — dead code and orphaned artifacts removed**

- Deleted orphaned `novel_testbed_app/` directory (contained only a stale `.pytest_cache` artifact with no source files)
- Removed `InferredModuleContract` data class from `novel_testbed/inference/types.py` — the type was defined but never instantiated in production code; `InferredState` and `require_keys` are the only runtime-used exports
- Removed two corresponding dead tests (`test_inferred_module_contract_defaults`, `test_inferred_module_contract_custom_confidence`) from `tests/inference/test_types.py` and updated the import block
- Final test count: **95 tests, all passing**

## 2026-03-06

**Comprehensive refactor, design-pattern overhaul, and documentation refresh** (commit `85e9879`)

- Applied Strategy, Template Method, Protocol, and Chain-of-Responsibility patterns across the pipeline
- Fixed critical `LLMSegmenter` bug: was accessing a private attribute (`inferencer.client`) on a class that stores it as `_client`, and calling a method (`complete`) that did not exist — redesigned `LLMSegmenter` to accept a client object directly via dependency injection
- Added `complete(prompt)` method and `_extract_text()` static helper to `OpenAILLMClient`, eliminating duplicated response-walking logic
- Resolved layering violation: removed module-level imports of inference-layer classes from `segmenter.py`; replaced with a local import inside `LLMSegmenter.__init__`
- Fixed `--llm` CLI flag: now correctly constructs `OpenAILLMClient` and passes it to `LLMSegmenter(client=...)`
- Fixed `pyproject.toml` packaging: changed `packages = ["novel_testbed"]` to `packages.find` so all sub-packages are included in distribution builds
- Fixed logger misconfiguration in `auto_contract.py` (spurious `addHandler` + `propagate` calls removed)
- Added full Sphinx-format doc comments to `llm_client.py`, `llm_inferencer.py`, `assessor.py`, and `rules.py`; added PEP 8 parameter name consistency
- Added `inline_list_comprehension` in `assessor.report_to_json`, removing an unnecessary nested function
- Created new test modules: `tests/segmentation/test_llm_segmenter.py` (7 tests), `tests/inference/test_prompts.py` (7 tests), `tests/inference/test_types.py` (10 tests), `tests/utils/test_source_fingerprint.py` (8 tests); expanded `tests/core/test_cli.py` with 7 new CLI tests
- Rewrote `docs/software-design.md` with full architecture diagrams, pattern inventory, and layering rules
- Updated `docs/api-inference.md`, `docs/api-segmentation.md`, `docs/index.md`, `mkdocs.yml`
- Added `Roadmap.md` (8-phase plan) and updated `README.md`, `README-cli.md`, `README-docs.md`

---

## Summary: Planned Phases

| Phase | Focus | Status |
|-------|-------|--------|
| v1.0 | Core pipeline: segment → parse → infer → assess | **Done** |
| Phase 2 | Richer assessment rules (flat arcs, threat peaks, agency collapse) | Planned |
| Phase 3 | Human-readable reports and pressure-curve visualization | Planned |
| Phase 4 | Alternative inference backends (Anthropic, NLP, local models) | Planned |
| Phase 5 | Multi-chapter and multi-file support | Planned |
| Phase 6 | Editor integrations (VS Code, Obsidian, Scrivener) | Planned |
| Phase 7 | Extended `ReaderState` schema | Planned |
| Phase 8 | Calibration and feedback loop | Planned |

See the full roadmap file for detailed descriptions of each phase.
