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

This tool helps you answer questions like:

- “Does this scene raise tension or just describe it?”
- “Did power actually shift, or did I only talk about power?”
- “Is this chapter doing something new, or circling the same emotional space?”
- “Am I escalating the story, or comforting myself?”

It does not tell you *what* to write.  
It tells you whether what you wrote **acts**.



## Reader Response measurement

For writers, you can read that as:

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

Everything else is just structure.



## A typical workflow

### 1. Write your novel in Markdown

You divide your book into chapters and modules:

```markdown
# Chapter One

## Scene Arrival
She stepped onto the sand.

## Exposition History
The island had once been occupied.
```

Each `##` heading marks a moment where something should happen to the reader.



### 2. Run inference (optional but powerful)

```bash
novel-testbed infer novel.md -o contract.yaml
```

This asks the system to read your scenes and *guess* what they are doing:

- What emotional movement is happening?
- Is danger rising?
- Is agency shrinking?
- Is trust forming?
- Is the genre shifting?

You get a filled-in contract as a starting point, not a verdict.  
Think of it as a first reader who never gets tired.



### 3. Read the contract like you would read margin notes

A module might look like:

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

You are not being graded.  
You are being asked:

> “Is this true?”

If the answer is no, either:
- the scene isn’t doing enough
- or the contract is wrong

Both are useful discoveries.



### 4. Assess your book

```bash
novel-testbed assess contract.yaml -o report.json
```

If you get a failure, it usually means:

> “You said something changed, but your own data says nothing changed.”

That is not condemnation.  
That is clarity.

It means the scene may be emotionally inert, even if it is beautifully written.



## What this is *not*

This is not:

- a style checker  
- a grammar checker  
- a literary judge  
- a replacement for intuition  

It does not know if your writing is “good.”  
It knows whether your writing **moves the reader state**.

Those are different things.



## Why this can feel uncomfortable

Writers are trained to trust:
- instinct
- rhythm
- tone
- resonance

This tool asks you to also trust:
- consequence
- progression
- pressure
- transformation

It does not replace intuition.  
It sharpens it.

If your book already works, this system will show you *why*.  
If it doesn’t, it will show you *where*.



## Think of this as choreography

You are not measuring art.  
You are measuring motion.

A dancer does not ask:
> “Was that beautiful?”

First they ask:
> “Did I move where I intended?”

This tool is asking that question for your story.

Everything else is yours.