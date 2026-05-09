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

## Query patterns by research intent

| Intent              | Query                              | Domain filtering                                   |
|---------------------|------------------------------------|----------------------------------------------------|
| Library docs        | `{lib} {concept} documentation`    | `allowed_domains: ["{lib-docs-domain}"]`           |
| GitHub issues       | `{org}/{repo} {concept}`           | `allowed_domains: ["github.com"]`                  |
| GitHub discussions  | `{org}/{repo} {topic} discussion`  | `allowed_domains: ["github.com"]`                  |
| Changelog/migration | `{lib} breaking changes migration` | `allowed_domains: ["github.com"]`                  |
| Stack Overflow      | `{error or concept} {lang}`        | `allowed_domains: ["stackoverflow.com"]`           |
| Design patterns     | `{pattern} guide tutorial {lang}`  | `blocked_domains: ["w3schools.com", "medium.com"]` |
| RFC/specs           | `{protocol} RFC specification`     | `allowed_domains: ["rfc-editor.org", "ietf.org"]`  |

## Slot sources

| Slot                               | Source                                                                                        |
|------------------------------------|-----------------------------------------------------------------------------------------------|
| `{lib}`, `{org}`, `{repo}`         | Lockfile / manifest, or extracted from GitHub URLs the user provides                          |
| `{concept}`, `{method}`, `{topic}` | Feature seed discussion and codebase findings                                                 |
| `{error}`                          | User's description or error messages found in codebase                                        |
| `{lang}`                           | Inferred from repo's primary language                                                         |
| `{lib-docs-domain}`                | Check actual docs domain — not all are `.com` (e.g. `docs.effect.website`, `docs.python.org`) |

## Steps

1. **Identify research intents** from brainstorm direction and codebase findings.
2. **Fill slots** from lockfile/manifest, GitHub URLs, discussion context. Check actual docs domain TLDs.
3. **Construct 2-4 focused queries** — plain keywords + at most one operator. Use `allowed_domains` / `blocked_domains` for domain filtering instead of stacking `site:` operators.
4. **Include filled queries in Explore subagent prompt.** Agent executes searches, cross-references results, returns synthesis.
5. **Fallback:** if <2 useful results, simplify — drop operators, broaden keywords. Report what was tried so the next attempt doesn't repeat failed queries.

Prefer fewer, sharper queries over many broad ones.
