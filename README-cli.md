# CLI Usage

This app treats your novel like a system that either changes something or wastes space.  
Each scene is evaluated as a transformation of reader state: before and after.  
If nothing changes, the scene failed. No mysticism, no vibes, no “but it felt important.”  
Just movement or dead weight.

You write prose.  
The CLI turns that prose into structure, intent, and tests.

Your novel is compiled through stages:

```
Markdown → Segment → Parse → Infer → Assess
```

This is not a parser.  
It is a narrative compiler.

Writers use this tool to expose weak scenes, false momentum, and structural stagnation.  
It doesn’t judge style. It judges consequence.



## Commands

The Novel Testbed CLI now provides **four** commands:

| Command  | Purpose |
|---------|--------|
| `segment` | Convert raw prose into structured Markdown |
| `parse`   | Build a blank contract YAML from structured Markdown |
| `infer`   | Build a populated contract using an LLM |
| `assess`  | Validate a contract against narrative rules |

The CLI is intentionally thin.  
All real logic lives in the domain modules.



## Invoking the CLI

If installed as a script entrypoint:

```bash
novel-testbed --help
```

If running directly from the repo:

```bash
python3 -m novel_testbed.cli --help
```



## Input format

You may provide:

1. **Raw prose Markdown**  
2. **Already-annotated Markdown**

If structure is missing, the **segmenter will create it**.  
If structure exists, it will be preserved.

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
It is load-bearing.



## 1. Segment: Create structure

```bash
novel-testbed segment novel.md -o annotated.md
```

Converts raw prose into annotated Markdown:

- Adds `# Chapter`
- Adds `## Scene`, `## Exposition`, etc.

This is your structural normalization phase.



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

This is your **spec file**.  
Nothing passes until you fill it in.



## 3. Infer: Automatically build a full contract (LLM-powered)

```bash
novel-testbed infer novel.md \
    --annotated annotated.md \
    -o contract.yaml
```

Pipeline:

```
Markdown → Segment → Parse → LLM → Contract YAML
```

The `--annotated` flag persists the segmented Markdown so you can:

- Inspect structure
- Commit structure
- Diff structure

Each module is filled with:

- pre_state
- post_state
- expected_changes
- fantasy alignment
- threat/agency levels

You now have a **book compiler**.



## OpenAI API Key (for `infer`)

The `infer` command requires an OpenAI API key.

It must be provided as:

```
OPENAI_API_KEY
```

Never in code.  
Never in YAML.  
Never in Git.

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

If missing, inference will refuse to run.

That is intentional.



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

Translation:

You promised movement.  
The data says stagnation.  
Fix or delete.



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

The engine only cares whether they change.



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

You are not building a parser.  
You are building a **narrative linter**.



## Logging

```python
logging.getLogger("novel_testbed")
```

Debug:

```bash
novel-testbed --log-level DEBUG assess contract.yaml
```

You will see:

- which modules fire which rules
- why failures occur
- where structure breaks