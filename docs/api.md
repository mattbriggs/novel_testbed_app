# API Reference

This section is generated directly from Python docstrings using `mkdocstrings`.

It reflects the *actual* public surface of the system.  
If something is missing here, it is not part of the real API.

This is intentional.



## Core Models

Data structures that define the shape of the narrative system.

::: novel_testbed.models

These classes form the semantic backbone of the application:

- `Module` → atomic unit of fiction  
- `Novel` → collection of modules  
- `ReaderState` → reader response model  
- `ModuleContract` → executable narrative specification  



## Parser

Structural front-end: Markdown → Novel → Modules.

::: novel_testbed.parser.base

::: novel_testbed.parser.commonmark

The parser layer is intentionally mechanical.  
It does not interpret meaning. It only finds joints.



## Contracts

Contract generation and serialization.

::: novel_testbed.contracts.contract

This module creates the specification that everything else operates on.  
The contract is the system.



## Assessment Engine

Rule-based narrative validation.

::: novel_testbed.contracts.assessor

::: novel_testbed.contracts.rules

This is where narrative intent becomes falsifiable.  
All future intelligence lives here.



## Inference Layer (LLM-backed)

Semantic front-end: Novel → Contract via Reader Response inference.

::: novel_testbed.inference.base

::: novel_testbed.inference.llm_client

::: novel_testbed.inference.llm_inferencer

::: novel_testbed.inference.auto_contract

These modules allow the system to *read* a novel and produce a contract
without author annotation.

They do not replace authorship.  
They expose it.



## CLI

Command-line orchestration.

::: novel_testbed.cli

The CLI is intentionally thin.  
It wires together the parser, inferencer, and assessment engine.

No logic should live here.



## Logging

Centralized logging configuration.

::: novel_testbed.logging_config

All modules are expected to emit meaningful, structured log messages.  
Debugging narrative structure should be observable, not mystical.



## Design Contract

This API reference is not documentation theater.

It is:

- mechanically generated
- version-controlled
- always consistent with the code

If the API changes, this page changes.  
If this page is wrong, the code is wrong.