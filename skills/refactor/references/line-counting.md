# Line Counting Rules

Functional lines = total lines minus:
- Blank lines (`^\s*$`)
- Comment-only lines (language-specific: `//`, `#`, `/* */`, `"""`, etc.)
- Lines that are purely formatter output (auto-added by prettier/black/gofmt that wouldn't exist in compact style are still structural — count them)

Quick count for common languages:
- JS/TS/Java/C: `grep -cv '^\s*$\|^\s*//' <file>`
- Python/Ruby/Shell: `grep -cv '^\s*$\|^\s*#' <file>`
- Rust/Go: `grep -cv '^\s*$\|^\s*//' <file>`

These slightly overcount (miss multi-line comment blocks) but are consistent and fast.
