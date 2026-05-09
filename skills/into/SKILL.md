---
name: into
description: Brainstorming partner that drives deep discussion about an idea before any code is written. Through natural conversation, explores the codebase and the web in parallel, challenges assumptions, and converges on a single well-specified ticket with structured description. Use when user invokes `/tap-into`, says "brainstorm", "let's think through X", "scope this out", "I want to build X but let's talk first", or has a `.tap/` directory and a feature ask they want to explore before committing.
---
<phase name="back-at-it">
  <purpose>
    Stress-test that new feature idea of their. 
    Run this command `git log --since=1.week --oneline | wc -l`. If the number is superior or equal to 100, proceed with this phase, otherwise go directly to `<phase name="understanding">`. 
    Always surface this phase when the number is over or equal to 100 AND when the user is discussing a feature implementation. If the count is under 100 or when the user is talking about refactoring, fixing or documenting something, stay silent and move on to `<phase name="understanding">`. 
  </purpose>
  <step name="aftermath">
    Ask the user why a new feature again, because he's got `echo "$(git log --since=1.week --oneline | wc -l) commits since last week"`, maybe they should slow the fuck down a little.
    Ask the user what is the purpose of this new feature? Probe them to tell you if it has added value at all.
  </step>
  <step name="wait">
    Wait. Let the user answers your questions before you continue.
    If the user comes to the conclusion that indeed this new feature is not needed, you can close this ideation session and invoke the Skill(refactor) instead; a good refactoring session can always be great. Otherwise, if the feature really has added value, proceed with the next phase: `<phase name="understanding">`
  </step>
</phase>
<phase name="understanding">
  <purpose>
    Understand the current project's context. First, follow the `<steps>`, wait for each Agent to finish their explorations, then ask questions to the user one at the time to refine the idea provided. 
    Once you understand what you're building, present the design intent & wait for the user's approval before continuing to the `<phase name="ideation">`.
  </purpose>

  <steps>
    You can spawn as many Agents of each of these types as you want: `<step name="websearch">`, `<step name="codebase_exploration">` & `<step name="patterns_discovery">`, depending on the complexity. If for example you need 2 "codebase_exploration" agents, 2 "patterns_discovery" agents & 2 "websearch" agents for a feature, that's fine. It doesn't have to be locked at specifically 3 agents.
    Each and everyone of them should be contained to their own tasks: 
    <step name="websearch"> 
      Agent(
        subagent_type: "Explore",
        description: "<3-5 word task summary>",
        prompt: "Research <topic> for <reason> with the WebSearch & WebFetch tools. Use the [dorks](dorks.md) for query construction. Cross reference findings accross sources. 
        ---
        Return your findings following this structure: 
          <findings>
            <fact_one url="url-one" />
            <fact_two url="url-two" />
            <fact_n url="url-n" />
            ...
          </findings>
          <patterns>
            How the community/docs recommand approaching this problem. 
          </patterns>
          <pitfalls>
            Known limitations, breaking changes, github issues related to the subject, deprecated software, ..
          </pitfalls>
          <open-notes>
            What you found interesting related to the topic researched
          </open-notes>
          <source>
            <url> - <one line why it mattered>
          </source>
        "
      )
    </step>
    <step name="codebase_exploration">
      Agent(
        subagent_type: "Explore",
        description: "<3-5 word task summary>",
        prompt: "
          Run baseline scans:
          - Pain markers: !`grep -rniE '(//|#|/\*|\*)\s*(TODO|FIXME|HACK|WORKAROUND)\b|@[Dd]eprecated\b' --exclude-dir={node_modules,dist,build,vendor,.git,.tap,docs,.claude}`
          - Git track: !`git log --since=1.week --stat` — where work concentrates, what stale
          - Project manifest: read package.json / Cargo.toml / go.mod / pyproject.toml / build.gradle / pom.xml. Map deps, versions, surprises
          - Topic surface: grep <topic> keywords, locate entry points, list files touched
          Then deep-dive based on findings (pick from menu, not all):
          - Call graph for <topic> — who calls what, types flowing
          - Test coverage near <topic> — colocated / tests/ / __tests__ / *_test.* / *.spec.*
          - Error handling patterns in area
          - Complexity hotspots — largest files by LOC near <topic>
          - Prior attempts — git log for partial/reverted similar work
          - Domain context — read .tap/domain/ if exists, map bounded contexts touched
          - **Dependency internals** — when <topic> touches a third-party dependency, dig INTO git-ignored directories where the ecosystem caches dependency source code. First identify the ecosystem from the project manifest, then locate the dep source:
            - JS/TS: `node_modules/<dep>/`
            - Rust: `.cargo/registry/src/` or `vendor/`
            - Python: `.venv/lib/*/site-packages/<dep>/` or `vendor/`
            - Go: `vendor/` or `GOPATH/pkg/mod/`
            - Java/Kotlin: `~/.m2/repository/` or `.gradle/caches/`
            - Ruby: `vendor/bundle/`
            - Other: check the lockfile or build output for the local cache path
            Once located:
            - Read the dep's entry point or public module — the file the project actually imports from
            - Trace the specific function/type/trait/class the project uses — read its implementation, not just its signature
            - Identify the dep's paradigm: sync/async, error model (exceptions / result types / error codes), concurrency model
            - Read the dep's CHANGELOG, README, or migration guide for version-specific behavior and deprecations
            - **ALWAYS skip `.env`, `.env.*`, credentials, secrets, tokens, API keys, or auth config files**
            - Keep reads targeted — entry point + the specific symbol the project uses. Do not scan the entire dependency tree.
          Return to main agent in this structure:
            ## Topic Surface
            - Entry points: <file:line>
            - Key files: <file> — <one-line role>
            ## Current State
            - <how it works today, with file:line refs>
            ## Pain Markers
            - <TODO/FIXME with file:line and 1-line summary>
            ## Git Energy
            - Hot files (last 2w): <file> (<N commits>)
            - Stale areas: <path> (last touched <date>)
            ## Tests
            - Coverage: <what tested, what not, with paths>
            ## Dependency Internals
            - <dep name> <version> — <what was learned from reading source>
            - Paradigm: <sync/async, concurrency model>
            - Error model: <exceptions / result types / error codes / panics>
            - Gotchas from source: <surprising behavior, undocumented constraints>
            ## Gotchas
            - <surprising state, broken assumptions, version mismatch>
            ## Open Questions
            - <what couldn't be resolved by scan — needs user input>
            ## Files Read
            - <path> — <why>
            Hard cap: 500 words. Bullets > prose. file:line refs mandatory.
        "
      )
    </step>
    <step name="patterns_discovery">
      Agent(
        subagent_type: "general-purpose",
        model: "sonnet",
        description: "Pattern recognition scan",
        prompt: "Scan the codebase for structural patterns relevant to the <topic>, plus established design patterns from the web. New modules must compose with neighbors, not against them.
        Codebase scan pattern recognition (Grep, Glob, Read):
        - Neighboring modules to <topic area> — what shapes recur
        - Paradigm signals — FP/OOP/mixed, from imports and idioms
        - Recurring shapes:
          - service/provider pairs
          - higher-order strategy
          - discriminated unions + exhaustive match
          - pipeline composition
          - smart constructors
          - stream processing
          - scoped resource lifecycle
        - Naming conventions, module layout, test colocation
        Web scan (WebSearch, WebFetch — use [dorks](dorks.md)):
        - refactoring.guru for canonical pattern names + tradeoffs
          allowed_domains: ['refactoring.guru']
        - martinfowler.com for enterprise patterns
          allowed_domains: ['martinfowler.com']
        - Language-idiomatic patterns (effect docs, Rust nomicon, etc.) for <lang>
        Cross-reference: which web pattern matches each codebase shape. Name them.
        Return to main agent in this structure:
        ## Codebase Patterns
        - <pattern name> — <where, file:line> — <one-line how used>
        ## Paradigm
        - <FP / OOP / mixed> — evidence: <imports, idioms>
        ## Convention Match
        - <topic concept> → <existing pattern in repo> — compose this way
        ## Web Patterns Considered
        - <pattern> [source: <url>] — fits / partial / no — <why>
        ## Anti-patterns Nearby
        - <shape to avoid, with file:line> — <why it's a smell>
        ## Recommendation Shape
        - New <topic> module should follow <pattern> because <reason from neighbors>
        ## Sources
        - <url> — <one-line why>
        Hard cap: 500 words. Every codebase claim cites file:line. Every web claim cites url."
      )
    </step>
  </steps>
  <done>
    This phase ends when every agent have returned consistent data accross all three steps. 
  </done>
</phase>

<phase name="ideation">
  <purpose>
    Deep conversation & collaboration with the user to create a ideation.md file that crystallize every decision made.
  </purpose>
  Based on the findings returned by `<step name="websearch">`, `<step name="codebase_exploration">` & `<step name="patterns_discovery">`, proceed with the ideation by writing a new ticket following the [ideation template](ideation-template.md) at `.tap/tickets/<slug>/ideation.md`. You don't have all the information yet, that is to be expected. The ideation will help filling in the gaps. 
  Do not invent informations that you don't yet have because false information is worse than no information at all. Do no rush convergence on this phase. 

  <steps>
    <step name="assess">
      Assess the scope first before asking any questions because if a description maps to multiple independent systems, it will need to be decomposed further. Scope that is too wide is to be decomposed into smaller sub-scope. 
    </step>
    <step name="decomposition">
      If a scope is too large for a single ticket, help the user decompose into sub-tickets through the normal `<ideation-flow>`. Each scope gets its own ticket & tap run lifecycle.
      
      **Stub deferred tickets immediately.** Once the user confirms the decomposition, create a minimal `ideation.md` for each deferred ticket BEFORE diving into the first ticket's full ideation. This ensures nothing falls through the cracks — `ls .tap/tickets/` always shows the full roadmap.

      Stub format:
      ```markdown
      # [<Feature Name>]: Design intent

      <!-- TODO: Full ideation pending — run /tap-into to complete -->

      ## Intent
      <one-line description of what this ticket delivers>

      ## Depends on
      - <slug of prerequisite ticket(s)>

      ## Context (from decomposition)
      - <bullet points captured during the scope discussion>
      - <relevant findings from the exploration agents>
      - <key constraints or decisions that affect this ticket>
      ```

      The stub is intentionally minimal — it preserves context from the decomposition discussion without inventing design decisions. The full ideation happens later via a separate `/tap-into` session.
    </step>
    <step name="questioning">
      Ask questions one at the time. Prefer multiple choices questions, but free-form questions are alright aswell. If a <topic> needs more exploration, break it into subsequent questions. Focus on understanding: purpose, constrainst, and what "done" should look like. 
    </step>
    <step name="approaches">
      When exploring `<approach>`, propose 2-5 different approaches with trade-offs for each. 
      Present them like the following:
      ```markdown
        [{0N}]: <approach title>
          - <approach description>
          - Tradeoffs:
            - <tradeoff one>
            - <tradeoff two>
            - <tradeoff n> 
          - Recommanded <approach title>: <why>
      ```
    </step>
    <step name="presentation">
      Once you believe that you understand the design, surface it to the user. for each section, scale the explanation based on its complexity and propose design patterns surfaced in `<step name="patterns_discovery">` that could match. 
      For each section, ask if its looks right or not. 
      Each section should cover architecture, components and/or modules, data flow, how errors are handled and test cases. 
      This is the step where you have to be ready to go back and forth with the user until you've converged. That's to be expected. 
    </step>
  </steps>
  <done>
    This phase ends when you and the user have reached an agreement on what the idea should look like.
    The user should be one signalling that this is phase is over. Once you've converged, move on to the <next-step>
  </done>
</phase>

<ideation-flow>
  General flow of the ideation process: 
  ```dot
    digraph ideation_flow {
      rankdir=TB;
      node [fontname="Helvetica"];
      "Synthesize Explore results\n(websearch + codebase + patterns)" [shape=box];
      "Draft ticket skeleton\n(known sections only,\nno invented info)" [shape=box];
      "Gaps in required sections?" [shape=diamond];
      "Ask clarifying questions\n" [shape=box];
      "Propose 2-3 approaches\n(grounded in patterns scan +\nneighboring conventions)" [shape=box];
      "User picks approach?" [shape=diamond];
      "Fill ## Intent, ## Context,\n## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries" [shape=box];
      "Two-implementations test\n(can two valid builds satisfy?)" [shape=diamond];
      "Tighten ambiguity\n(pin the choice)" [shape=box];
      "Present design sections" [shape=box];
      "User approves design?" [shape=diamond];
      "Emit ticket to\n.tap/tickets/<slug>/ideation.md" [shape=box];
      "ticket self-review\n(schema + ## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries, ## Open decisions,\n## Considered & rejected, ## Failure modes,\n## Sources)" [shape=box];
      "Issues found?" [shape=diamond];
      "Fix inline" [shape=box];
      "User reviews ticket?" [shape=diamond];
      "Emit final ticket emission following the [ideation template](ideation-template.md)" [shape=doublecircle];
      "Synthesize Explore results\n(websearch + codebase + patterns)"
        -> "Draft ticket skeleton\n(known sections only,\nno invented info)"
        -> "Gaps in required sections?";
      "Gaps in required sections?" -> "Ask clarifying questions\n" [label="yes"];
      "Ask clarifying questions\n" -> "Gaps in required sections?";
      "Gaps in required sections?" -> "Propose 2-3 approaches\n(grounded in patterns scan +\nneighboring conventions)" [label="no"];
      "Propose 2-3 approaches\n(grounded in patterns scan +\nneighboring conventions)" -> "User picks approach?";
      "User picks approach?" -> "Propose 2-3 approaches\n(grounded in patterns scan +\nneighboring conventions)" [label="reject all,\nmore options"];
      "User picks approach?" -> "Fill ## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries, ## Open decisions,\n## Considered & rejected, ## Failure modes,\n## Sources" [label="picks one"];
      "Fill ## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries" -> "Two-implementations test\n(can two valid builds satisfy?)";
      "Present design sections" -> "User approves design?";
      "User approves design?" -> "Present design sections" [label="no, revise"];
      "User approves design?" -> "Emit ticket to\n.tap/tickets/<slug>/ideation.md" [label="yes"];
      "Emit ticket to\n.tap/tickets/<slug>/ideation.md"
        -> "ticket self-review\n(schema + ## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries, ## Open decisions,\n## Considered & rejected, ## Failure modes,\n## Sources)"
        -> "Issues found?";
      "Issues found?" -> "Fix inline" [label="yes"];
      "Fix inline" -> "ticket self-review\n(schema + ## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries, ## Open decisions,\n## Considered & rejected, ## Failure modes,\n## Sources)";
      "Issues found?" -> "User reviews ticket?" [label="no"];
      "User reviews ticket?" -> "Fill ## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries, ## Open decisions,\n## Considered & rejected, ## Failure modes,\n## Sources" [label="changes requested"];
      "User reviews ticket?" -> "Emit final ticket emission following the [ideation template](ideation-template.md)" [label="approved"];
    }
  ```

  The final state is a fully fledged ticket containing everyting that has been discussed here. 
</ideation-flow>

<general-rules>
  These rules apply accross all <phases> & <steps> :
    - Always ask one question at a time because more than one question will overwhelm the user. 
    - Always prefer multi-choice questions over free-from questions because they're easier to answer.
    - Always validate incrementally because this is a slow process. A proper laid out design will produce better result than an poorly laid out one. 
    - Always value flexibity because the <phases> & <steps> can be interchangeable. Structured ideas will surface from chaos. Going back & forth is expecteed.
    - Always value simplicity over over-engineered ideations because elegance emerge from simple & readable code, not over-engineered code. Good code is not measured by how many lines it contains. 
</general-rules>

<next-step>
  Once in this section, immediately invoke Skill(convey, <slug>) where `<slug>` is the ticket slug from the ideation just completed.
</next-step>