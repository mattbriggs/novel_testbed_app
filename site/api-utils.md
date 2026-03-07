# API: Utils

Source fingerprinting and provenance utilities.

::: novel_testbed.utils.source_fingerprint

This module binds a generated narrative contract to a specific version of a Markdown source file. It prevents silent drift between a contract and the text it was generated from.

It provides:
- Cryptographic hashing of source files
- Provenance metadata for contract YAML
- A foundation for detecting stale or mismatched contracts

This is the system’s chain-of-custody layer.



## `compute_sha256(path: Path) -> str`

Compute the SHA-256 hash of a file.

Reads the file in chunks to support large manuscripts without loading them fully into memory.

**Parameters**

- `path`  
  Path to the file to hash.

**Returns**

- Hexadecimal SHA-256 digest string.

**Raises**

- `FileNotFoundError` if the file does not exist  
- `IOError` if the file cannot be read

**Purpose**

Used to verify that a stored Markdown source has not changed since a contract was generated.



## `build_source_metadata(original_path: Path, copied_path: Path, text: str) -> dict`

Build provenance metadata for embedding in a contract YAML file.

This metadata binds the contract to:
- The original input file
- The copied canonical source
- The exact text content
- The moment of generation

**Parameters**

- `original_path`  
  Path to the user-supplied Markdown file.

- `copied_path`  
  Path where the canonical copy was stored.

- `text`  
  Full Markdown content used to generate the contract.

**Returns**

A dictionary suitable for embedding under a top-level `source` key in the contract YAML:

```yaml
source:
  original_path: /path/to/novel.md
  copied_path: output/source.md
  sha256: "9b3a2c..."
  generated_at: "2026-01-18T21:43:12.521Z"
```

**Purpose**

Allows the system to:
- Detect if a contract is stale
- Guarantee reproducibility
- Treat narrative input as immutable build input



In normal human terms:

This module is what stops your contract from becoming fiction about your fiction.