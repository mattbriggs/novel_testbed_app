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

The testbed exists to make that visible.



## The pipeline

The system is now strictly staged:

```
Markdown → Segment → Parse → Infer → Assess
```

Each step has one responsibility:

| Stage   | Purpose |
|--------|--------|
| Segment | Create structure |
| Parse   | Read structure |
| Infer   | Interpret meaning |
| Assess  | Validate change |

No command performs another stage’s work.  
No stage hides inside another.



## The first step: segmentation

Before anything else happens, your text must be **segmented**.

Segmentation means:

- Raw prose becomes structured Markdown
- Chapters (`#`) are explicit
- Modules (`## Scene`, `## Exposition`, `## Transition`) are explicit
- The book becomes mechanically parseable

Run it:

```bash
novel-testbed segment novel.md -o annotated.md
```

This produces a version of your book with all structural joints visible.

You should open this file and read it.  
This is your narrative skeleton.

If segmentation is wrong, everything downstream is unreliable.



## Reader Response measurement

For writers, read this as:

> **Reader Response Pattern**

A Reader Response Pattern is a recurring emotional or psychological effect:

- “Truth is exposed.”
- “Someone gains power.”
- “Safety is lost.”
- “Agency collapses.”
- “Danger becomes unavoidable.”

These are not tropes.  
They are emotional consequences.

Your scenes activate these whether you intend them to or not.  
The system simply asks you to name them.



## How a writer uses the tool

You do not need to think like a programmer.  
You only need to answer three questions per scene:

1. What does the reader feel or believe before?
2. What does the reader feel or believe after?
3. What changed?

Everything else is scaffolding.



## A typical workflow

### 1. Write your novel

Raw prose is fine:

```markdown
She stepped onto the sand. The wind was sharp.
```

Or structured Markdown:

```markdown
# Chapter One

## Scene Arrival
She stepped onto the sand.
```



### 2. Segment your novel

```bash
novel-testbed segment novel.md -o annotated.md
```

Now you have explicit structure.  
Fix chapters. Rename scenes. Insert exposition.  
This is mechanical, not artistic.



### 3. Parse structure into a blank contract

```bash
novel-testbed parse annotated.md -o contract.yaml
```

This creates your narrative worksheet.

Nothing is judged yet.  
You are declaring intent.



### 4. Infer reader response (semantic pass)

```bash
novel-testbed infer annotated.md -o contract.yaml
```

Important:
- `infer` does **not** segment
- `infer` expects already-annotated Markdown
- Structure must exist before inference

What happens here:

1. The structure is parsed
2. An LLM infers:
   - pre_state
   - post_state
   - expected_changes
3. A populated contract is written

The LLM is acting like a tireless first reader, not a critic.



### 5. Read the contract like margin notes

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

This is a question, not a verdict:

> “Is this true?”



### 6. Assess your book

```bash
novel-testbed assess contract.yaml -o report.json
```

A failure usually means:

> “You promised movement, but your own data shows none.”

That is not criticism.  
That is precision.



## What this is not

This is not:

- a style checker  
- a grammar checker  
- a literary judge  
- a replacement for intuition  

It does not know if your writing is “good.”  
It knows whether your writing **moves the reader state**.



## Why this works

Writers trust:

- instinct  
- rhythm  
- resonance  

This system adds:

- consequence  
- escalation  
- pressure  
- transformation  

It does not replace intuition.  
It makes intuition visible and testable.



## Think of this as choreography

You are not measuring art.  
You are measuring motion.

A dancer does not ask:

> “Was that beautiful?”

First they ask:

> “Did I move where I intended?”

This tool asks that question of your story.

Everything else remains yours.
