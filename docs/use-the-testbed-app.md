# Use the Testbed App

Writers are allergic to words like *metrics*, *validation*, and *contract* for a reason. They sound like accounting. This tool is not here to turn your novel into a spreadsheet. It is here to give you something writers almost never get: a way to see whether a scene actually *moves* the reader.

Think of this less as unit testing and more as **Reader Response mapping**.

You are not measuring quality.  
You are measuring *effect*.

Did the reader’s sense of danger increase?  
Did power shift?  
Did trust erode?  
Did intimacy grow?  
Did the genre tilt?  
Did something destabilize?

That is what this system tracks.

Not beauty.  
Not voice.  
Not talent.  
Change.



## What this tool really does

Every scene or block of exposition in your novel is treated like a moment of transformation:

```
Reader Before → Reader After
```

If a scene does not change anything in the reader, then it is decorative. It might be lovely. It might be lyrical. But structurally, it is inert.

The testbed exists to make that visible, without romance or apology.



## The new first step: segmentation

Before anything else happens, your text is **segmented**.

That means:

- Raw prose is turned into structured Markdown
- Chapters (`#`) and modules (`## Scene`, `## Exposition`, `## Transition`) are inserted
- The book becomes mechanically parseable

This is now the real pipeline:

```
Markdown → Segment → Parse → Infer → Assess
```

Segmentation is compilation.  
If structure is wrong, nothing downstream is trustworthy.

You can run it explicitly:

```bash
novel-testbed segment novel.md -o annotated.md
```

This produces a version of your book with all structural joints marked.  
You can open it, read it, and correct it. This is your mechanical skeleton.



## Reader Response measurement

For writers, read this as:

> **Reader Response Pattern**

A Reader Response Pattern is a recurring emotional or psychological effect a story can have:

- “Truth is exposed.”
- “Someone gains power.”
- “Safety is lost.”
- “Belonging is created.”
- “Agency collapses.”
- “Danger becomes unavoidable.”

These are not tropes.  
They are **emotional consequences**.

Your scenes activate these whether you intend them to or not.  
This system simply asks you to be honest about which ones you are using.



## How a writer uses the tool

You do not need to think like a programmer.  
You only need to answer three questions per scene:

1. What does the reader believe or feel *before* this scene?
2. What does the reader believe or feel *after* this scene?
3. What changed?

That’s it.

Everything else is just scaffolding so the system can check your answers.



## A typical workflow

### 1. Write or import your novel

It can be raw prose or already structured Markdown. The system will normalize it.

```markdown
She stepped onto the sand. The wind was sharp.
```

or:

```markdown
# Chapter One

## Scene Arrival
She stepped onto the sand.
```



### 2. Segment your novel (optional but clarifying)

```bash
novel-testbed segment novel.md -o annotated.md
```

This gives you a visible structural map.  
You can fix chapter boundaries, rename scenes, or add exposition modules by hand.



### 3. Run inference (semantic pass)

```bash
novel-testbed infer novel.md \
  --annotated annotated.md \
  -o contract.yaml
```

Now inference does four things:

1. Segments your text  
2. Parses the structure  
3. Infers reader state changes  
4. Writes:
   - a contract (`contract.yaml`)
   - and optionally the annotated Markdown (`annotated.md`)

The LLM is not judging you.  
It is acting as a tireless first reader.



### 4. Read the contract like margin notes

```yaml
pre_state:
  emotional_tone: calm
  threat_level: 0.1
  agency_level: 0.9

post_state:
  emotional_tone: unease
  threat_level: 0.4
  agency_level: 0.85

expected_changes:
  - "Threat increases"
  - "Control becomes fragile"
```

This is not a grade.  
It is a question:

> “Is this true?”

If not, either the scene is weak or the interpretation is wrong.  
Both are useful discoveries.



### 5. Assess your book

```bash
novel-testbed assess contract.yaml -o report.json
```

If a scene fails, it usually means:

> “You said something changed, but your own data says nothing changed.”

That is not judgment.  
That is precision.



## What this is *not*

This is not:

- a style checker  
- a grammar checker  
- a literary judge  
- a replacement for intuition  

It does not know if your writing is “good.”  
It knows whether your writing **moves the reader state**.

Those are different questions. One is taste.  
The other is mechanics.



## Why this can feel uncomfortable

Writers trust:

- instinct  
- rhythm  
- tone  
- resonance  

This system asks you to also trust:

- consequence  
- escalation  
- pressure  
- transformation  

It does not replace intuition.  
It makes intuition accountable.



## Think of this as choreography

You are not measuring art.  
You are measuring motion.

A dancer does not ask:

> “Was that beautiful?”

First they ask:

> “Did I move where I intended?”

This tool is asking that question for your story.

Everything else is yours.