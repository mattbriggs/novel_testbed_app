# Documentation (MkDocs)

This project uses **MkDocs** with Mermaid and mkdocstrings.

Docs are built from:

- `docs/*.md`
- Python docstrings (Sphinx style)
- Mermaid.js diagrams

## Install documentation dependencies

Use the project requirements:

```bash
pip install -r requirements.txt
```

If you maintain separate optional doc dependencies later, keep them aligned here.

## Serve docs locally

```bash
mkdocs serve
```

Open:

```
http://127.0.0.1:8000/
```

Changes to documentation files or Python code will live-reload.

## Build static site

```bash
mkdocs build
```

Output is generated in:

```
site/
```

This directory can be deployed to GitHub Pages or any static web host.

## Generate the class diagram of the software object model

Because drawing UML by hand is cosplay.

We auto-generate it from code so the diagram cannot lie.

### 1. Install dependencies

Add to `requirements.txt`:

```
pylint>=3.0
```

You also need **Graphviz**, which pyreverse uses to render diagrams.

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

From the project root:

```bash
pyreverse -o svg -p novel_testbed novel_testbed/
```

Produces:

- `classes_novel_testbed.svg`
- `packages_novel_testbed.svg`

### 3. Store diagrams in the docs tree

```bash
mkdir -p docs/diagrams
mv classes_novel_testbed.svg docs/media/classes_novel_testbed.svg
mv packages_novel_testbed.svg docs/media/packages_novel_testbed.svg
```

### 4. Reference diagrams in docs

```markdown
## Class Diagram

This diagram is mechanically derived from the codebase.

![Class Diagram](media/classes_novel_testbed.svg)
```

Optional:

```markdown
## Package Diagram

![Package Diagram](media/packages_novel_testbed.svg)
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
