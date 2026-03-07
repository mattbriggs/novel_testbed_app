# Documentation (MkDocs)

This project uses **MkDocs** with the Material theme, Mermaid diagrams,
and `mkdocstrings` for auto-generated API reference from Python docstrings.

Docs are built from:

- `docs/*.md` — hand-written guides and architecture pages
- Python docstrings (Sphinx-compatible `:param:` / `:return:` style)
- Mermaid.js diagrams embedded in Markdown



## Install documentation dependencies

Use the project requirements:

```bash
pip install -r requirements.txt
```

Or install the docs extras directly:

```bash
pip install -e ".[docs]"
```



## Serve docs locally

```bash
mkdocs serve
```

Open:

```
http://127.0.0.1:8000/
```

Changes to documentation files or Python docstrings will live-reload.



## Build static site

```bash
mkdocs build
```

Output is generated in:

```
site/
```

This directory can be deployed to GitHub Pages or any static web host.



## Documentation structure

```
docs/
├── index.md                    # Home page and conceptual overview
├── software-design.md          # Architecture, patterns, design rationale
├── use-the-testbed-app.md      # How-to guide for authors
├── tool-walkthrough.md         # Step-by-step CLI walkthrough
├── how-to-manually-segment.md  # Guide for hand-annotating Markdown
├── diagram-class.md            # Auto-generated class diagram
├── diagram-package.md          # Auto-generated package diagram
├── api.md                      # API reference index
├── api-core.md                 # Core models and CLI
├── api-inference.md            # Inference layer
├── api-segmentation.md         # Segmentation layer
├── api-parser.md               # Parser layer
├── api-contracts.md            # Contracts and assessment
└── api-utils.md                # Utility functions
```

Navigation is configured in `mkdocs.yml`.



## Generate UML diagrams

Diagrams are auto-generated from code so they cannot drift.

### 1. Install dependencies

```bash
pip install pylint
brew install graphviz        # macOS
sudo apt install graphviz   # Ubuntu
```

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
mv classes_novel_testbed.svg docs/media/classes_novel_testbed.svg
mv packages_novel_testbed.svg docs/media/packages_novel_testbed.svg
```

### 4. Reference diagrams in docs

```markdown
![Class Diagram](media/classes_novel_testbed.svg)
```

Regenerate after every major refactor.
If the diagram looks wrong, the code is wrong.



## Docstring standard

All public modules and methods use Sphinx-compatible format:

```python
def my_function(arg: str) -> int:
    """
    One-line summary.

    Extended description if needed.

    :param arg: Description of the argument.
    :return: Description of the return value.
    :raises ValueError: When the input is invalid.
    """
```

`mkdocstrings` reads these and renders them in the API reference.



## Roadmap

The future development roadmap is tracked in [Roadmap.md](Roadmap.md).
