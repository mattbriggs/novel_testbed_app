# Step-by-step workflow for a writer using Novel Testbed

This is a step-by-step guide for writers who want to use the tool without thinking like a programmer. It focuses only on what you need to do and why you are doing it, so you can concentrate on improving your writing rather than on technical details.

## 1) Put your draft in Markdown (raw is fine)

Create a file like `novel.md`.

You *can* write it already structured:

```markdown
# Chapter One

## Scene Arrival
She stepped onto the sand.

## Exposition History
The island had once been occupied.
```

Rules:
- `#` = chapter
- `##` = a unit you want to evaluate (scene/exposition/transition)
- Everything under a `##` belongs to that module until the next `##`

But you **don’t have to**. If your draft is raw prose with no headings, the tool can now create structure for you.



## 2) (New) Segment the draft into parseable modules

Segmentation is the new first stage. It inserts `#` and `##` markers so the parser can do its job.

Run:

```bash
novel-testbed segment novel.md -o annotated.md
```

What you get:
- `annotated.md` that contains explicit `# Chapter` and `## Scene/Exposition/Transition`
- Your original prose preserved, just wrapped in joints

This is the simplest way to see “what the tool thinks your modules are.”  
If you hate the boundaries, fix them here. You’re allowed.



## 3) Parse the book into a blank contract (structure only)

Now you have two options:

### Option A: parse your original (if it’s already structured)

```bash
novel-testbed parse novel.md -o contract.yaml
```

### Option B: parse the annotated Markdown (recommended if you used `segment`)

```bash
novel-testbed parse annotated.md -o contract.yaml
```

Either way, you just created your **contract file**: a worksheet for what each module does to the reader.

At this point nothing is evaluated yet. You just generated the template.



## 4) Choose your approach: manual contract or LLM-assisted contract

### Option A: Manual (slow, precise)
You fill in `contract.yaml` yourself.

### Option B: Inferred (fast, surprisingly useful)
Let the tool create a first-pass contract.

**If your input is already structured Markdown:**

```bash
novel-testbed infer novel.md -o contract.yaml
```

**If your input might be raw prose, or you want the annotated output saved:**

```bash
novel-testbed infer novel.md \
  --annotated annotated.md \
  -o contract.yaml
```

What inference attempts to infer:
- reader emotional tone
- threat level and agency level
- power balance
- genre drift
- expected reader-response changes

Treat this like notes from a blunt first reader, not divine truth.



## 5) Read the contract module-by-module

Open `contract.yaml`. For each module, look at:

- `pre_state` (how the reader is positioned before)
- `post_state` (how the reader is positioned after)
- `expected_changes` (what you intended to shift)

You’re asking one question:

> “Is this what the scene actually does?”

If the contract is wrong, fix the contract.  
If the contract is right but embarrassing, fix the scene.



## 6) Make the reader-state fields feel natural

Don’t overthink it. Use plain language.

Example fields:

```yaml
pre_state:
  emotional_tone: calm
  threat_level: 0.1
  agency_level: 0.8
  power_balance: self

post_state:
  emotional_tone: unease
  threat_level: 0.4
  agency_level: 0.7
  power_balance: environment

expected_changes:
  - "Threat rises"
  - "Control weakens"
```

If numbers make you itchy:
- Think of `0.1` as “low”
- `0.5` as “medium”
- `0.9` as “high”

You’re not doing math. You’re recording pressure.



## 7) Run an assessment pass

```bash
novel-testbed assess contract.yaml -o report.json
```

This produces a report with:
- PASS / WARN / FAIL per module
- findings explaining what triggered the result



## 8) Interpret failures like a revision assistant, not a verdict

A typical FAIL means:

- You declared change, but pre_state == post_state

Translation:

> “You promised movement but your own description says nothing changed.”

That usually points to one of these issues:
- the scene is static
- the scene repeats an earlier beat
- the scene is atmospheric but not consequential
- the scene contains movement but you didn’t capture it in the contract



## 9) Revise with a clear target

Pick one failing or warning module. Then choose *one* fix:

- **Increase pressure** (raise threat, reduce agency, tighten power)
- **Clarify power** (who has leverage now?)
- **Change emotional temperature** (calm → dread, hope → disgust)
- **Advance reader knowledge** (reveal, confirm, mislead)
- **Cut the module** (if it’s a loop)

Then update either:
- the manuscript
- or the contract
- or both



## 10) Re-run the loop

After changes:

```bash
novel-testbed assess contract.yaml -o report.json
```

You’re looking for:
- fewer FAILs
- fewer WARNs
- clearer intent

This is iterative revision, just with receipts.



## 11) Use it as a map of the whole book

Once the contract is decent, it becomes a high-level lens:

- Where does threat spike?
- Where does the genre shift?
- Where does power flip?
- Where does the book stall?

This is the part that feels like having x-ray vision, minus the radiation lawsuit.



## Suggested routine (simple and realistic)

- If your draft is raw prose: run `segment` once and keep `annotated.md` as your “structured draft.”
- Run `infer` once to get a starting contract (and save annotated output with `--annotated`).
- Fix the contract until it matches your intent.
- Run `assess` after each revision session.
- Focus only on FAILs first.
- Treat WARNs as “notes,” not problems.



## The point

This tool doesn’t replace intuition.  
It forces your intuition to make a claim you can check:

> “This scene changes the reader.”

Then it asks: *prove it.*