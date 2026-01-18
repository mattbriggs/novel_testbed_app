# Novel Testbed

A unit-test harness for novels.  
It treats a work of fiction as a system that must transform reader state, module by module.

If a scene doesn’t change power, tension, genre, or emotional stakes, it fails.  
No vibes. No glossing. Just execution.

This tool is designed to make narrative intent explicit and falsifiable, in the same way unit tests do for software.

You are not “expressing yourself.”  
You are running a system.  
This tells you whether the system moves.



## Core idea

Each scene or exposition block is treated as a function:

```mermaid
flowchart LR
    A[Reader State Before] --> M[Module / Scene] --> B[Reader State After]
```

If nothing changes, the module failed its job.

The system enforces three things:

1. You must declare what each module intends to do.  
2. You must declare how the reader’s state changes.  
3. The system verifies that your declared intent is structurally coherent.

This does not judge your prose.  
It judges whether your prose *does anything*.



## Architecture

The system is now a true pipeline:

```
Raw Markdown
      ↓
Segmentation (adds chapters & modules)
      ↓
Parsing (builds structural modules)
      ↓
Inference (builds narrative contracts)
      ↓
Assessment (validates narrative movement)
```

Think of it like a compiler:

| Phase | Role |
|------|------|
| `segment` | Creates structure |
| `parse` | Builds an AST |
| `infer` | Adds semantics |
| `assess` | Performs static analysis |

You are no longer “writing Markdown.”  
You are compiling narrative intent.



## Installation

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

Run tests:

```bash
pytest
```

If tests fail, the book cannot be tested.



## Markdown conventions

After segmentation, the system expects CommonMark-style structure:

```markdown
# Chapter Title

## Scene 1
Text...

## Exposition 1
Text...

## Transition 1
Text...
```

| Markdown | Meaning |
|--------|--------|
| `# Title` | Chapter |
| `## Scene ...` | Scene module |
| `## Exposition ...` | Exposition module |
| `## Transition ...` | Optional transition module |

Everything between two `##` headings is treated as one module.

If your text lacks this structure, the **segmenter** will create it.  
If you supply it, the system will respect it.

The parser is strict on purpose.  
Structure is not decoration here. It is load-bearing.



## Workflow Overview

There are now **four** major workflows:

| Command | Purpose |
|------|------|
| `segment` | Turn raw prose into structured Markdown |
| `parse` | Structural parsing only (blank contract) |
| `infer` | Structural + semantic inference |
| `assess` | Validate a contract against narrative rules |

Pipeline view:

```
segment → parse → infer → assess
```

Or as a compiler:

```
segment → AST → semantic model → static analysis
```



## Tests

Run everything:

```bash
pytest
```

Covered:

- Segmentation (raw prose → structured Markdown)
- Markdown parsing
- Contract generation
- Contract loading
- YAML round-trips
- Rule evaluation
- CLI parsing
- LLM inference (fully stubbed)

If the tests fail, the book is structurally unsound.

That is not metaphorical.



## Philosophy

Most novels are evaluated by:

- tone  
- voice  
- prestige  
- vibes  

This tool evaluates:

- structural movement  
- power shifts  
- narrative pressure  
- declared intent vs effect  

It does not care if your sentences are beautiful.  
It cares if they *move the system*.

Art happens inside constraints.  
This tool makes the constraints explicit.