# API: Core Models

Data structures that define the shape of the narrative system.

::: novel_testbed.models

These classes form the semantic backbone of the application:

- `Module` → atomic unit of fiction  
- `Novel` → collection of modules  
- `ReaderState` → reader response model  
- `ModuleContract` → executable narrative specification  

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
