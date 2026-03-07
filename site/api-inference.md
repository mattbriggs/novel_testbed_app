# API: Inference Layer

Semantic front-end: Novel → Contract via Reader Response inference.

The inference layer converts parsed `Module` objects into fully populated
`ModuleContract` objects. It can operate via LLM API calls or any
`ContractInferencer` implementation.

---

## Abstract interface

::: novel_testbed.inference.base

---

## LLM client

::: novel_testbed.inference.llm_client

The client exposes two call patterns:

- `complete(prompt)` — raw text response (used by `LLMSegmenter`)
- `infer_json(user_prompt=...)` — structured JSON response (used by `OpenAIContractInferencer`)

---

## LLM inferencer

::: novel_testbed.inference.llm_inferencer

Reader state is **chained** across modules: the `post_state` of module N
becomes the `pre_state` of module N+1, so the reader's accumulated state is
preserved across the full novel.

---

## High-level pipeline helper

::: novel_testbed.inference.auto_contract

This is the recommended entry point for the `infer` CLI command. It handles
parse → infer orchestration in one call.

---

## Prompt construction

::: novel_testbed.inference.prompts

Prompts are deterministic templates. The `SYSTEM_PROMPT` instructs the model
to return only valid JSON. `build_module_prompt` constructs the per-module
user prompt from structural metadata and prose text.

---

## Inference types

::: novel_testbed.inference.types

These frozen dataclasses define the validated intermediate representation
between the raw LLM response and the final `ModuleContract`. They are not
exposed in the public API but are used internally by `OpenAIContractInferencer`.

---

These modules allow the system to *read* a novel and produce a contract
without manual author annotation.

They do not replace authorship.
They expose it.
