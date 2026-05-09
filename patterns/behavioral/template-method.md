---
name: template-method
category: behavioral
aliases: [template-pattern]
intent: >-
  Define the skeleton of an algorithm in a base class, deferring some steps to subclasses without changing its structure
sources:
  - https://refactoring.guru/design-patterns/template-method
smells_it_fixes:
  - duplicate-algorithm-variants
  - long-method
  - shotgun-surgery
smells_it_introduces:
  - inappropriate-intimacy
  - speculative-generality
composes_with:
  - strategy
  - factory-method
  - hook-method
clashes_with:
  - god-class
test_invariants:
  - "The template method invokes abstract steps in the documented sequence"
  - "A subclass override of one hook does not affect the execution of other hooks"
  - "The overall algorithm structure is the same across all subclasses"
  - "Hook methods with default implementations can be overridden without affecting required steps"
---

# Template Method

## Intent

Define the skeleton of an algorithm in an operation, deferring some steps to subclasses. Template Method lets subclasses redefine certain steps of an algorithm without changing the algorithm's structure. The base class controls the high-level flow; subclasses supply the variant pieces via abstract or overridable hook methods.

## Structure

```
AbstractClass
  + templateMethod(): void     // FINAL — controls flow
      { step1()                // invariant
        step2()                // abstract — subclass must provide
        hook()                 // optional override — has default
        step3() }              // invariant

  # step1(): void     { /* invariant impl */ }
  # abstract step2(): void
  # hook(): void      { /* default no-op or default behavior */ }
  # step3(): void     { /* invariant impl */ }

ConcreteClassA extends AbstractClass {
  step2(): void { /* variant A */ }
}

ConcreteClassB extends AbstractClass {
  step2(): void { /* variant B */ }
  hook(): void  { /* override default */ }
}
```

Roles:
- **AbstractClass** — defines the template method and declares abstract/hook steps
- **ConcreteClass** — implements the abstract steps; may override hooks
- **Template method** — the fixed sequence; typically marked final to prevent override
- **Hook** — optional override point with a default implementation

## Applicability

- Multiple classes implement the same algorithm with only certain steps differing
- Common behavior should be factored up to avoid duplication, with variation points isolated
- Framework design: base class defines application flow; subclasses fill in domain-specific steps
- Data processing pipelines, report generators, test fixtures (setUp/tearDown), parsers

## Consequences

- **Code reuse** — invariant algorithm steps live once in the base class
- **Inversion of control** — the framework calls subclass code, not the other way around ("Hollywood Principle")
- **Controlled extension points** — hooks and abstract methods define exactly where variation is allowed
- **Inheritance coupling** — subclasses are tightly bound to base class internals; changes to the template affect all subclasses
- **Override proliferation** — many hooks can be hard to track; subclasses may override things they shouldn't
- **Depth limit** — deep inheritance trees make template chains hard to follow
- **Strategy often preferred** — favors composition over inheritance for the same variability

## OOP shape

```
abstract class DataImporter {
  // Template method — sealed
  final import(source: Source): Report {
    const raw = this.readData(source)       // abstract
    const validated = this.validate(raw)    // abstract
    this.onBeforeStore(validated)           // hook — default no-op
    const stored = this.storeData(validated)
    return this.buildReport(stored)         // abstract
  }

  protected abstract readData(source: Source): RawData
  protected abstract validate(data: RawData): ValidData
  protected abstract buildReport(stored: StoredData): Report
  protected abstract storeData(data: ValidData): StoredData

  protected onBeforeStore(_data: ValidData): void {} // hook
}

class CsvImporter extends DataImporter {
  protected readData(source: Source): RawData { /* CSV parse */ }
  protected validate(data: RawData): ValidData { /* CSV validation */ }
  protected storeData(data: ValidData): StoredData { /* store */ }
  protected buildReport(s: StoredData): Report { /* report */ }
}
```

## FP shape

```
// Template method = higher-order function with injected steps
type ImportSteps<Raw, Valid, Stored> = {
  readData:    (source: Source) => Raw
  validate:    (raw: Raw) => Valid
  storeData:   (valid: Valid) => Stored
  buildReport: (stored: Stored) => Report
  onBeforeStore?: (valid: Valid) => void  // optional hook
}

const importTemplate =
  <R, V, S>(steps: ImportSteps<R, V, S>) =>
  (source: Source): Report => {
    const raw     = steps.readData(source)
    const valid   = steps.validate(raw)
    steps.onBeforeStore?.(valid)
    const stored  = steps.storeData(valid)
    return steps.buildReport(stored)
  }

// Variant = pass a different steps object (like Strategy but with the skeleton fixed)
const csvImport = importTemplate({ readData: parseCsv, validate: validateCsv, ... })
```

## Smells fixed

- **duplicate-algorithm-variants** — near-identical algorithm implementations across subclasses are collapsed; only the varying steps remain in each subclass
- **long-method** — a monolithic method that handles every variant via conditionals is replaced by a template that delegates variation to subclass hooks
- **shotgun-surgery** — a change to the algorithm skeleton that previously required edits in every variant class now requires only a change in the base class template

## Tests implied

- **Step sequence** — instrument each step with a spy; call the template method; assert the spies fired in exact documented order
- **Hook isolation** — override one hook in a subclass and verify no other hook's behavior changes; steps are independent
- **Structural invariance** — two concrete subclasses both invoke the template and produce outputs whose structural shape (report schema, step count) is identical, even though step implementations differ
- **Default hook passthrough** — a concrete subclass that does not override a hook receives the default behavior; verify default is exercised

## Sources

- https://refactoring.guru/design-patterns/template-method
