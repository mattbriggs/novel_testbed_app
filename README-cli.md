# CLI Usage

The Novel Testbed treats your novel as a system of transformations.
Each scene must move the reader from one state to another. If nothing changes,
the scene is structurally inert.

You write prose.  
The CLI turns prose into structure, intent, and verification.

Your novel is compiled through explicit stages:

```
Markdown → Segment → Parse → Infer → Assess
```

This is not a parser.  
It is a narrative compiler.



## Commands

The Novel Testbed CLI provides four commands:

| Command   | Purpose |
|----------|--------|
| `segment` | Convert raw prose into structured Markdown |
| `parse`   | Build a blank contract YAML from structured Markdown |
| `infer`   | Populate a contract using an LLM |
| `assess`  | Validate a contract against narrative rules |

Each command has one responsibility.  
No command performs another’s work.



## Invoking the CLI

If installed as an entrypoint:

```bash
novel-testbed --help
```

From the repo:

```bash
python3 -m novel_testbed.cli --help
```



## Input format

There are two kinds of Markdown:

1. **Raw prose Markdown** → must go through `segment`
2. **Annotated Markdown** → used by `parse` and `infer`

Canonical structure:

```markdown
# Chapter Title

## Scene 1
Text...

## Exposition 1
Text...

## Transition 1
Text...
```

Everything between two `##` headings is one module.

Structure is not decoration.  
It is the grammar of your book.



## 1. Segment: Create structure

```bash
novel-testbed segment novel.md -o annotated.md
```

Purpose:
- Insert chapter headings if missing
- Insert at least one module
- Normalize structure

Output is always annotated Markdown.

This step is mechanical and deterministic unless `--llm` is used.

```bash
novel-testbed segment novel.md -o annotated.md --llm
```



## 2. Parse: Build a blank contract

```bash
novel-testbed parse annotated.md -o contract.yaml
```

Produces a blank narrative contract:

```yaml
modules:
  - module_id: M001
    chapter: The Sea
    module_title: Scene 1
    module_type: scene
    anchors:
      start: I stood on the deck…
      end: The horizon went black.
    pre_state: {}
    post_state: {}
    expected_changes: []
```

This is your **specification file**.
Nothing is evaluated yet. You are declaring intent.



## 3. Infer: Populate the contract (LLM-powered)

```bash
novel-testbed infer annotated.md -o contract.yaml
```

Pipeline:

```
Annotated Markdown → Parse → LLM → Contract YAML
```

Important:
- `infer` does **not** segment
- `infer` expects already-annotated Markdown
- Structure must exist before inference

Each module is filled with:

- pre_state
- post_state
- expected_changes
- fantasy alignment
- threat / agency levels

This step converts structure into meaning.



## OpenAI API Key (for `infer`)

The `infer` command requires an OpenAI API key:

```
OPENAI_API_KEY
```

Set it:

macOS / Linux:
```bash
export OPENAI_API_KEY="sk-..."
```

Windows:
```powershell
setx OPENAI_API_KEY "sk-..."
```

Verify:

```bash
echo $OPENAI_API_KEY
```

If the key is missing, inference refuses to run.



## 4. Declare reader state and intent

Each module defines:

```yaml
pre_state:
  genre: survival
  power_balance: environment
  emotional_tone: controlled
  threat_level: 0.2
  agency_level: 0.9

post_state:
  genre: survival
  power_balance: environment
  emotional_tone: unease
  threat_level: 0.4
  agency_level: 0.85

expected_changes:
  - "Threat level increases"
  - "Comfort becomes fragile"
```

If you cannot state what changed, the scene is unfinished.



## 5. Assess the novel

```bash
novel-testbed assess contract.yaml -o report.json
```

Output:

```json
[
  {
    "module_id": "M004",
    "severity": "FAIL",
    "findings": [
      {
        "rule": "no_change",
        "severity": "FAIL",
        "message": "pre_state equals post_state but expected_changes declared."
      }
    ]
  }
]
```

Interpretation:
- You declared change
- The state data shows none
- The scene is structurally inert



## Reader State Model

```python
ReaderState:
  genre: str
  power_balance: str
  emotional_tone: str
  dominant_fantasy_id: str
  threat_level: float   # 0..1
  agency_level: float   # 0..1
```

Extend freely:

- suspicion_level  
- captivity_pressure  
- moral_distortion  
- trust_erosion  

The engine only cares that values move.



## Assessment Rules

Rules live in:

```
novel_testbed/contracts/rules.py
```

Each rule returns:

- PASS  
- WARN  
- FAIL  

Current rules:

| Rule | Result |
|------|------|
| Missing reader state | WARN |
| Missing expected changes | WARN |
| Declared change but no state difference | FAIL |

This is not a style checker.  
It is a **structural integrity checker** for narrative movement.



## Logging

Enable debug logging:

```bash
novel-testbed --log-level DEBUG assess contract.yaml
```

You will see:

- which modules fired which rules
- why failures occurred
- where structure or intent collapsed
```
