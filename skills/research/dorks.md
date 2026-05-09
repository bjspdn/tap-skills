# Web Search Reference

**STOP CHECK:** Read this file before constructing any web search queries.

## Search engine

WebSearch uses the **Brave Search API**, not Google. Most Google dork operators silently fail or return degraded results. Use only Brave-compatible operators and patterns.

## Operator reference

| Operator             | Status | Notes                                                |
|----------------------|--------|------------------------------------------------------|
| `site:domain.com`    | works  | With plain keywords. Don't stack with exact phrases. |
| `"exact phrase"`     | works  |                                                      |
| `-term`              | works  |                                                      |
| `NOT`                | works  | Uppercase required                                   |
| `OR`                 | works  | Uppercase required                                   |
| `AND`                | works  | Uppercase required                                   |
| `inbody:"phrase"`    | works  |                                                      |
| `intitle:term`       | loose  | Matching is approximate                              |
| `filetype:` / `ext:` | works  |                                                      |
| `inurl:`             | dead   | Not supported                                        |
| `cache:`             | dead   |                                                      |
| `related:`           | dead   |                                                      |
| `link:`              | dead   |                                                      |
| `info:`              | dead   |                                                      |
| `~`                  | dead   |                                                      |
| `+`                  | dead   |                                                      |

## What works vs. what breaks

**Works:**
- `site:` + plain keywords
- One operator + keywords
- `NOT site:` for domain exclusion
- `OR` between keywords

**Breaks:**
- Stacking `site:` + multiple exact phrases
- 3+ operators chained together
- `inurl:` (not supported at all)
- Complex boolean chains

**Rule of thumb:** one domain operator + plain keywords. Keep queries simple.

## API-level filtering

WebSearch supports `allowed_domains` and `blocked_domains` parameters — more reliable than the `site:` operator. Prefer these when constructing Explore agent prompts that will use WebSearch.

## Query patterns by domain

### Library / Framework

| Intent              | Query                              | Domain filtering                                   |
|---------------------|------------------------------------|----------------------------------------------------|
| Library docs        | `{lib} {concept} documentation`    | `allowed_domains: ["{lib-docs-domain}"]`           |
| GitHub issues       | `{org}/{repo} {concept}`           | `allowed_domains: ["github.com"]`                  |
| GitHub discussions  | `{org}/{repo} {topic} discussion`  | `allowed_domains: ["github.com"]`                  |
| Changelog/migration | `{lib} breaking changes migration` | `allowed_domains: ["github.com"]`                  |
| Stack Overflow      | `{error or concept} {lang}`        | `allowed_domains: ["stackoverflow.com"]`           |
| Design patterns     | `{pattern} guide tutorial {lang}`  | `blocked_domains: ["w3schools.com", "medium.com"]` |
| RFC/specs           | `{protocol} RFC specification`     | `allowed_domains: ["rfc-editor.org", "ietf.org"]`  |

### Algorithm / Math

| Intent              | Query                                        | Domain filtering                                                     |
|---------------------|----------------------------------------------|----------------------------------------------------------------------|
| Algorithm overview  | `{algorithm} algorithm properties complexity` | `allowed_domains: ["wikipedia.org"]`                                 |
| Academic papers     | `{algorithm} {property} paper`               | `allowed_domains: ["arxiv.org", "scholar.google.com"]`               |
| Math reference      | `{concept} definition properties`            | `allowed_domains: ["mathworld.wolfram.com", "wikipedia.org"]`        |
| Reference impl      | `{algorithm} implementation {lang}`          | `allowed_domains: ["github.com"]`                                    |
| Complexity analysis | `{algorithm} time space complexity`          | `blocked_domains: ["geeksforgeeks.org"]`                             |
| Visualization       | `{algorithm} visualization interactive`      | `allowed_domains: ["visualgo.net"]`                                  |

### Game Systems

| Intent              | Query                                    | Domain filtering                                                              |
|---------------------|------------------------------------------|-------------------------------------------------------------------------------|
| Engine docs         | `{engine} {concept} documentation`       | `allowed_domains: ["{engine-docs-domain}"]`                                   |
| GDC talks           | `{topic} GDC talk`                       | `allowed_domains: ["gdcvault.com", "youtube.com"]`                            |
| Game dev patterns   | `{pattern} game development`             | `allowed_domains: ["gamedeveloper.com", "gamedev.stackexchange.com"]`         |
| Engine source       | `{engine} {system} source implementation`| `allowed_domains: ["github.com"]`                                             |
| Performance         | `{system} game performance benchmark`    | `blocked_domains: ["medium.com"]`                                             |

### Protocol / Standard

| Intent              | Query                                    | Domain filtering                                                  |
|---------------------|------------------------------------------|-------------------------------------------------------------------|
| RFC lookup          | `{protocol} RFC specification`           | `allowed_domains: ["rfc-editor.org", "ietf.org"]`                 |
| W3C specs           | `{standard} W3C specification`           | `allowed_domains: ["w3.org"]`                                     |
| IEEE standards      | `{standard} IEEE`                        | `allowed_domains: ["ieee.org", "ieeexplore.ieee.org"]`            |
| Reference impl      | `{protocol} reference implementation`   | `allowed_domains: ["github.com"]`                                 |
| Conformance         | `{protocol} conformance test suite`      | `allowed_domains: ["github.com"]`                                 |

### Software Patterns

| Intent              | Query                                    | Domain filtering                                                  |
|---------------------|------------------------------------------|-------------------------------------------------------------------|
| Pattern catalog     | `{pattern} design pattern`               | `allowed_domains: ["refactoring.guru"]`                           |
| Enterprise patterns | `{pattern} enterprise application`       | `allowed_domains: ["martinfowler.com"]`                           |
| Lang-idiomatic      | `{pattern} idiomatic {lang}`             | `allowed_domains: ["{lang-docs-domain}"]`                         |
| Style guides        | `{lang} style guide conventions`         | `blocked_domains: ["w3schools.com", "medium.com"]`                |

## Slot sources

| Slot                               | Source                                                                                        |
|------------------------------------|-----------------------------------------------------------------------------------------------|
| `{lib}`, `{org}`, `{repo}`         | Lockfile / manifest, or extracted from GitHub URLs the user provides                          |
| `{concept}`, `{method}`, `{topic}` | Research topic and context block                                                              |
| `{error}`                          | User's description or error messages found in codebase                                        |
| `{lang}`                           | Inferred from context block (project-bound) or user prompt (pure-knowledge)                   |
| `{lib-docs-domain}`                | Check actual docs domain — not all are `.com` (e.g. `docs.effect.website`, `docs.python.org`) |
| `{engine}`                         | Game engine name from user prompt or project deps                                             |
| `{engine-docs-domain}`             | Engine's docs site (e.g. `docs.godotengine.org`, `bevyengine.org/learn`)                      |
| `{algorithm}`                      | Algorithm name from user prompt                                                               |
| `{protocol}`, `{standard}`         | Protocol or standard name from user prompt                                                    |
| `{pattern}`                        | Design pattern name from research findings or user prompt                                     |
| `{property}`                       | Specific property being researched (e.g. "convergence", "period", "collision resistance")     |
| `{system}`                         | Game subsystem (e.g. "physics", "rendering", "ECS", "audio")                                  |

## Steps

1. **Identify research intents** from topic and domain classification.
2. **Fill slots** from context block, user prompt, lockfile/manifest. Check actual docs domain TLDs.
3. **Construct 2-4 focused queries** — plain keywords + at most one operator. Use `allowed_domains` / `blocked_domains` for domain filtering instead of stacking `site:` operators.
4. **Include filled queries in Explore subagent prompt.** Agent executes searches, cross-references results, returns synthesis.
5. **Fallback:** if <2 useful results, simplify — drop operators, broaden keywords. Report what was tried so the next attempt doesn't repeat failed queries.

Prefer fewer, sharper queries over many broad ones.
