# How to manually segment your novel

Manual segmentation means adding **chapter and module headings** to your draft so Novel Testbed can treat it like a sequence of testable units.

A **module** is one chunk you want the system to evaluate: a scene, an exposition block, or a transition.

When you’re done, the file should be valid CommonMark Markdown and should feed directly into:

- `novel-testbed parse …`
- `novel-testbed infer …`
- `novel-testbed assess …`

## What the system expects

Use Markdown headings:

- `#` = Chapter
- `##` = Module boundary (Scene / Exposition / Transition)

Everything under a `##` heading belongs to that module **until the next `##`** (or the next chapter).

### Accepted module headings

Start module titles with one of these keywords:

- `## Scene …`
- `## Exposition …`
- `## Transition …`

The parser infers type from the **first word** of the module title. If it doesn’t start with those words, it becomes `OTHER` (which is allowed, but less useful).

## Step-by-step manual segmentation

### Step 1: Put the draft in a single Markdown file

Create `novel.md` (or any `.md`).

If your draft is currently raw paragraphs, that’s fine.

### Step 2: Add chapter markers with `#`

Every time the story clearly moves to a new chapter (or you want a major structural division), insert:

```markdown
# Chapter Title
```

If your book doesn’t really have chapters yet, you can use:

- `# Chapter One`
- `# Chapter Two`
- or even `# Draft` (yes, it’s allowed, the point is structure)

### Step 3: Identify module boundaries with `##`

A module boundary is where you want to “reset the microscope.”

Common boundaries:
- time jump
- location change
- POV change
- a new beat begins (problem introduced, pressure escalates, confrontation starts)
- exposition interrupts action
- a bridging/transition passage happens

Insert one of these:

```markdown
## Scene Arrival
## Exposition History
## Transition Aftermath
```

### Step 4: Keep each module’s text under its heading

Don’t nest scenes inside scenes. Don’t put `##` headings mid-module unless you want a new module.

### Step 5: Sanity-check the structure

A valid segmented file has this basic shape:

```markdown
# Chapter Something

## Scene Something
(text)

## Exposition Something
(text)
```

That’s it. No special formatting beyond headings.

---

## Example: before and after

### Before (raw prose, no structure)

```markdown
She stepped off the bus and into the heat. The town smelled like citrus and diesel.
At the corner store, the clerk watched her too closely. She bought water anyway.

The town had once been a grove, before the developers came. They drained the marsh
and buried the old foundations. Nobody talked about what they found.
```

### After (manually segmented, ready for Novel Testbed)

```markdown
# Chapter One

## Scene Arrival
She stepped off the bus and into the heat. The town smelled like citrus and diesel.
At the corner store, the clerk watched her too closely. She bought water anyway.

## Exposition The Town
The town had once been a grove, before the developers came. They drained the marsh
and buried the old foundations. Nobody talked about what they found.
```

Now the system can test whether **Scene Arrival** changes reader state, and whether **Exposition The Town** changes it again.

---

## How to choose “Scene” vs “Exposition” vs “Transition”

Use these rules (they’re practical, not philosophical):

### Scene
Use `## Scene …` when:
- something happens in real time
- characters act, decide, confront, react
- the reader’s pressure should move

### Exposition
Use `## Exposition …` when:
- you’re explaining context, history, systems, backstory
- the passage is primarily informational
- it reframes meaning more than it advances action

### Transition
Use `## Transition …` when:
- you’re bridging time/location/POV
- you’re compressing movement (“Three days later…”, “By winter…”, travel montage)
- it’s connective tissue, but still should shift state

If you’re unsure, default to **Scene**. You can always change labels later.

---

## Common mistakes that break segmentation

### Missing `##` headings
If you don’t add module headings, the parser will produce **0 modules**, and inference/assessment won’t have anything to work with.

### Using the wrong heading level
- `#` is for chapters
- `##` is for modules

If you use `###` for scenes, the parser won’t treat them as modules.

### Putting text above the first module
Avoid starting a chapter with prose before the first `##`. Put everything inside a module.

Bad:

```markdown
# Chapter One
This is prose with no module heading.
## Scene 1
…
```

Better:

```markdown
# Chapter One

## Scene Opening
This is the opening prose.
```

---

## A quick “ready to run” checklist

Before feeding the file to Novel Testbed:

- [ ] File is `.md`
- [ ] At least one `# Chapter …`
- [ ] At least one `## Scene …` / `## Exposition …` / `## Transition …`
- [ ] All prose is under a `##` module heading
- [ ] No `###` used for modules

If that’s true, your Markdown is ready to go through the system.

---