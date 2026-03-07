# API: Segmentation Layer

The segmentation layer is the structural front-end of Novel Testbed. Its job
is to take whatever prose you wrote and make it executable. That means inserting
explicit chapter and module boundaries so the parser and inference system have
something real to work with.

It does not analyze meaning.
It does not judge quality.
It only creates joints.

::: novel_testbed.segmentation.segmenter

---

## Core classes

### ModuleSegmenter

```python
class ModuleSegmenter:
    def segment_markdown(self, text: str, title: str) -> str:
        ...
```

Deterministic and conservative. Guarantees:

- A chapter header: `# <title>`
- At least one module: `## Scene 1`
- Correct ordering (chapter before modules)
- Idempotent for already-structured Markdown
- Always returns a trailing newline

### LLMSegmenter

```python
class LLMSegmenter(ModuleSegmenter):
    def __init__(self, client=None) -> None:
        ...
    def segment_markdown(self, text: str, title: str) -> str:
        ...
```

Uses an OpenAI-backed client to infer semantically appropriate boundaries.
Accepts any object with a `complete(prompt: str) -> str` interface.
If no client is provided, creates an `OpenAILLMClient` automatically.

---

## Behavior

| Input | Output |
|-------|--------|
| Raw prose | Markdown with `#` and `##` headers inserted |
| Already-structured Markdown | Returned unchanged (normalized) |
| Inverted structure (module before chapter) | Rebuilt in correct order |
| Empty input | Returns minimal valid structure |

Segmentation guarantees that downstream systems always receive valid
structural input. The parser never has to guess. The inferencer never
has to hallucinate boundaries.

---

## Design note

`LLMSegmenter` uses a **local import** to obtain `OpenAILLMClient` at
instantiation time. This keeps the segmentation layer independent of
the inference layer at module load time, preserving strict layering.

`LLMSegmenter` inherits `segment_markdown` override from `ModuleSegmenter`
(it does not call `super().segment_markdown()`). The LLM fully replaces the
deterministic logic for this call.

---

## Role in the pipeline

Segmentation is the guaranteed first phase:

```
Markdown → Segment → Parse → Infer → Assess
```

If segmentation fails, nothing downstream is trustworthy.

This is not decoration.
It is compilation.
