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

```
reader_state_before → reader_state_after
```

If nothing changes, the module failed its job.

The system enforces three things:

1. You must declare what each module intends to do.
2. You must declare how the reader’s state changes.
3. The system verifies that your declared intent is structurally coherent.

This does not judge your prose.  
It judges whether your prose *does anything*.



## Installation

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

If tests fail, the book cannot be tested.  
Yes, that is on purpose.



## Markdown conventions

The parser assumes CommonMark-style Markdown with strict structural conventions:

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

If you don’t mark your joints, the system cannot test your book.  
That is intentional.



## Workflow Overview

There are now **three** major workflows:

| Command | Purpose |
|------|------|
| `parse` | Structural parsing only (blank contract) |
| `infer` | Structural parsing + semantic inference (auto-filled contract) |
| `assess` | Validate a contract against narrative rules |

Think of them like compiler phases:

```
parse  → AST
infer  → semantic analysis
assess → static validation
```



## 1. Parse: Build a blank contract

```bash
novel-testbed parse novel.md -o contract.yaml
```

This generates a YAML contract skeleton:

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



## 2. Infer: Automatically build a full contract (LLM-powered)

```bash
novel-testbed infer novel.md -o contract.yaml
```

This does:

```
Markdown → parse → LLM inference → populated contract
```

Each module is analyzed and filled with:

- pre_state
- post_state
- expected_changes
- dominant fantasy (if any)
- threat/agency levels

This is the semantic front-end of the system.  
It turns text into executable narrative intent.

You now have a book compiler.



### OpenAI API Key (for `infer`)

The `infer` command uses an LLM to automatically populate your narrative contract.  
That requires an OpenAI API key.

This key is a **secret**. It does not belong in your repo.  
It does not belong in YAML.  
It does not belong in command history.

It belongs in your environment.

The application only reads the key from an environment variable named:

```
OPENAI_API_KEY
```

If that variable is not set, `novel-testbed infer` will refuse to run.

This is intentional.



#### 2.1. Get an API key

Create one at:

https://platform.openai.com/

It will look like:

```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Treat it like a password.



#### 2.2. Set the key in your environment

macOS / Linux (bash, zsh):

```bash
export OPENAI_API_KEY="sk-..."
```

Make it permanent:

```bash
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
source ~/.zshrc
```

Windows (PowerShell):

```powershell
setx OPENAI_API_KEY "sk-..."
```

Restart the terminal afterward.

Verify:

```bash
echo $OPENAI_API_KEY
```

If you see your key, you’re wired.

If you see nothing, inference will not run. That is correct behavior.



#### 2.3. Optional: Using a `.env` file (local only)

If you prefer a local file:

1. Create a `.env` file:

```bash
OPENAI_API_KEY=sk-...
```

2. Add this to `.gitignore`:

```
.env
```

Never commit it. Not once. Not accidentally.

This method is optional. The project works fine with plain environment variables.



#### 2.4. How the CLI uses the key

When you run:

```bash
novel-testbed infer novel.md -o contract.yaml
```

The CLI will:

1. Check for `OPENAI_API_KEY`
2. Refuse to run if it’s missing
3. Pass it only to the LLM client in memory
4. Never log it
5. Never write it to disk

If the key is missing, you’ll see:

```
ERROR: OPENAI_API_KEY is not set.
Set your API key using:

  export OPENAI_API_KEY="sk-..."

The key must not be stored in the repository.
```

That is not a suggestion. It is the contract.



#### 2.5. Why this matters

This tool treats narrative like software.  
Secrets must be treated like secrets.

If your novel leaks less than your infrastructure, something is backwards.



## 3. Declare reader state and intent (manual or inferred)

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

If you can’t say what changed, the scene doesn’t work yet.



## 4. Assess the novel

```bash
novel-testbed assess contract.yaml -o report.json
```

Example output:

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

Which means:

You promised movement.  
The data says stagnation.  
Fix or delete.



## Reader State Model

Each module works against this structure:

```python
ReaderState:
  genre: str
  power_balance: str
  emotional_tone: str
  dominant_fantasy_id: str
  threat_level: float   # 0..1
  agency_level: float   # 0..1
```

Extend it freely:

- suspicion_level
- captivity_pressure
- moral_distortion
- trust_erosion

The engine does not care what fields you add.  
It only cares whether they change.



## Assessment Rules

Rules live in:

```
novel_testbed/contracts/rules.py
```

Each rule evaluates one module and emits:

- PASS
- WARN
- FAIL

Current built-ins:

| Rule | Result |
|------|------|
| Missing reader state | WARN |
| Missing expected changes | WARN |
| Declared change but no state difference | FAIL |

This is where all intelligence lives.

You are not building a parser.  
You are building a narrative linter.



## Logging

The package logger:

```python
logging.getLogger("novel_testbed")
```

Run with debug logging:

```bash
novel-testbed --log-level DEBUG assess contract.yaml
```

You will see:

- which modules fire which rules
- why a failure occurred
- what was missing or contradictory



## Tests

Run everything:

```bash
pytest
```

Covered:

- Markdown parsing
- Contract generation
- Contract loading
- YAML round-trips
- Rule evaluation
- CLI parsing
- LLM inference (stubbed)

If the tests fail, the book is structurally unsound.



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

It doesn’t care if your sentences are beautiful.  
It cares if they *move the system*.

That is not anti-art.  
That is honesty.



## Build documentation

This project uses **MkDocs** with Mermaid and mkdocstrings.

Docs are built from:

- `docs/*.md`
- Python docstrings (Sphinx style)
- Mermaid.js diagrams

Serve locally:

```bash
mkdocs serve
```

Build static site:

```bash
mkdocs build
```



## Generate the class diagram of the software object model

Because drawing UML by hand is cosplay.

We auto-generate it from code so the diagram cannot lie.

### 1. Install dependencies

Add to `requirements.txt`:

```
pylint>=3.0
```

Install Graphviz:

macOS:
```bash
brew install graphviz
```

Ubuntu:
```bash
sudo apt install graphviz
```

Windows:
Install from https://graphviz.org and ensure `dot` is on PATH.

Verify:

```bash
dot -V
```



### 2. Generate diagrams

```bash
pyreverse -o svg -p novel_testbed novel_testbed/
```

Produces:

- `classes_novel_testbed.svg`
- `packages_novel_testbed.svg`



### 3. Store diagrams

```bash
mkdir -p docs/diagrams
mv classes_novel_testbed.svg docs/diagrams/classes.svg
mv packages_novel_testbed.svg docs/diagrams/packages.svg
```



### 4. Reference in docs

```markdown
## Class Diagram

This diagram is mechanically derived from the codebase.

![Class Diagram](diagrams/classes.svg)
```

Optional:

```markdown
## Package Diagram

![Package Diagram](diagrams/packages.svg)
```



### 5. Why this matters

These diagrams are not decorative.

They are:

- mechanically derived  
- impossible to drift  
- structurally authoritative  

If the diagram looks wrong, the code is wrong.  
Regenerate after every major refactor.

That is the contract.



This README now reflects what your system actually is:

Not a writing tool.  
Not an editor.  
Not a stylist.

A narrative compiler with static analysis and semantic inference.

And that is a much more dangerous thing.