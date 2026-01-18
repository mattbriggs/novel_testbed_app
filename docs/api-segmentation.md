## API Segmentation

The segmentation layer is the structural front-end of Novel Testbed. Its job is brutally simple: take whatever prose you wrote and make it executable. That means inserting explicit chapter and module boundaries so the parser and inference system have something real to work with.

It does not analyze meaning.  
It does not judge quality.  
It only creates joints.

::: novel_testbed.segmentation.segmenter

### Core Class

```python
class ModuleSegmenter:
    def segment_markdown(self, text: str, title: str) -> str:
        """
        Convert raw prose into annotated Markdown with structural markers.

        Returns Markdown that contains:
        - A chapter header:     # <title>
        - At least one module:  ## Scene / ## Exposition / ## Transition
        """
```

### Behavior

| Input | Output |
|------|-------|
| Raw prose | Markdown with `#` and `##` headers inserted |
| Already structured Markdown | Returned unchanged (idempotent) |
| Empty input | Still returns a valid minimal structure |

Segmentation guarantees that downstream systems always receive valid structural input. The parser never has to guess. The inferencer never has to hallucinate boundaries. Structure is always explicit.

### Default Strategy

The base `ModuleSegmenter` is deterministic and conservative:

- Adds a chapter using the provided title
- Creates a single `## Scene` if no modules exist
- Preserves original text verbatim inside the new structure
- Never destroys author-defined headings

It is intentionally dumb. That is a feature.

### Optional LLM Segmenter

You may implement:

```python
class LLMSegmenter(ModuleSegmenter):
    ...
```

which uses an LLM to infer:

- Scene boundaries
- Exposition vs action
- Transitions
- Structural pacing

This mirrors the design of the inference layer: strategy objects, not hard wiring.

### Role in the Pipeline

Segmentation is now the guaranteed first phase:

```
Markdown → Segment → Parse → Infer → Assess
```

If segmentation fails, nothing downstream is trustworthy.

This is not decoration.  
It is compilation.