# Novel Testbed

Novel Testbed is a test harness that treats a novel as an executable system.

It assumes a simple premise:  
fiction is not decoration. It is transformation.

Every scene, every block of exposition, every transition is supposed to *do*
something to the reader. Shift power. Increase pressure. Alter belief. Change
genre gravity. Disturb safety. Create threat. Create attachment.

If a module does not change reader state, it is inert.  
If it is inert, it is structural noise.

This system exists to make that visible.



This documentation covers:

- How a novel is parsed into structural modules
- How reader state is modeled
- How narrative contracts are declared
- How contracts can be inferred automatically using an LLM
- How module-by-module assessment works
- How failures are reported and interpreted

The system does not care if prose is beautiful.  
It cares if it *changes state*.



## Conceptual pipeline

```mermaid
flowchart TD
    A[Novel Markdown] --> B[Parser]
    B --> C1[Blank Contract YAML]
    C1 --> D1[Author Edits Contract]
    D1 --> E[Assessment Engine]
    E --> F[PASS / WARN / FAIL Report]

    B --> C2[LLM Inference Engine]
    C2 --> C3[Inferred Contract YAML]
    C3 --> E
```

There are two valid workflows:

1. **Author-declared contract**
   - You write the contract yourself.
   - You explicitly state what each module is supposed to do.
   - The system checks your honesty.

2. **LLM-inferred contract**
   - The system reads your novel and infers:
     - Reader state before and after each module
     - Intended change
     - Narrative pressure
   - You review, correct, and tighten.
   - The system becomes a semantic microscope.

Both paths converge on the same point:  
a contract that can be tested.



## What is being tested?

Each module is treated as a function:

```
ReaderState_before → ReaderState_after
```

If:

```
ReaderState_before == ReaderState_after
```

then the module failed to perform work.

Not artistically.  
Structurally.

This is not literary criticism.  
It is narrative mechanics.



## Reader State

Reader state is a model of how the reader is positioned:

- What genre they think they are in
- Who holds power
- How safe the world feels
- How much agency the protagonist has
- What emotional pressure exists

This is sometimes called *Reader Response* in literary theory.  
Here, it is treated as measurable state.

The system does not try to *interpret* your book.  
It tests whether your own declared interpretation is coherent.



## Why this exists

Most novels are evaluated by:

- tone
- prestige
- voice
- vibes

Novel Testbed evaluates:

- structural movement
- power dynamics
- narrative pressure
- declared intent vs actual effect

It does not ask if your sentences are pretty.  
It asks if your scenes are necessary.

That is a harder question.