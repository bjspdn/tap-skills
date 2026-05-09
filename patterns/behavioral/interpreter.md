---
name: interpreter
category: behavioral
aliases: [expression-evaluator]
intent: >-
  Define a grammar for a language and provide an interpreter that uses the grammar to process sentences
sources:
  - https://en.wikipedia.org/wiki/Interpreter_pattern
  - https://www.amazon.com/Design-Patterns-Elements-Reusable-Object-Oriented/dp/0201633612
smells_it_fixes:
  - long-conditional-chain
  - switch-on-type
  - duplicate-algorithm-variants
smells_it_introduces:
  - large-class
  - speculative-generality
composes_with:
  - composite
  - visitor
  - flyweight
  - iterator
clashes_with:
  - god-class
test_invariants:
  - "Each terminal expression evaluates to the same value for identical context inputs"
  - "Composite expressions delegate evaluation entirely to their sub-expressions"
  - "Context is not mutated by an expression except through defined assignment operations"
  - "Grammar trees composed from the same rules produce consistent parse results"
---

# Interpreter

## Intent

Given a language, define a representation for its grammar along with an interpreter that uses the representation to interpret sentences in the language. Each grammar rule maps to a class; sentences are represented as abstract syntax trees composed from those classes. Interpretation is a recursive traversal of the tree.

## Structure

```
AbstractExpression
  + interpret(context: Context): Value

TerminalExpression          NonterminalExpression
  (leaf — literal,            - children: AbstractExpression[]
   variable, literal num)     + interpret(context): Value
                                  { combines children.interpret(context) }

Context
  - bindings: Map<symbol, Value>
  + lookup(symbol): Value
  + assign(symbol, Value): void

Client
  - builds AST from grammar
  - calls root.interpret(context)
```

Roles:
- **AbstractExpression** — declares the interpret operation
- **TerminalExpression** — implements interpret for atomic symbols (literals, variables)
- **NonterminalExpression** — implements interpret for grammar rules; holds sub-expression children
- **Context** — carries global information needed during interpretation (variable bindings, I/O)
- **Client** — builds the AST and invokes interpretation

## Applicability

- The grammar is simple and well-bounded; performance is not the primary concern
- Efficiency is less important than extensibility of grammar rules
- Domain-specific languages (query languages, rule engines, expression evaluators, regular expressions)
- Sentences can be represented as abstract syntax trees and evaluated recursively
- The grammar rarely changes but new interpretations are added frequently

## Consequences

- **Easy to add new expressions** — each grammar rule is its own class; open/closed for grammar extension
- **Simple grammar implementation** — classes directly mirror grammar rules
- **Hard to maintain complex grammars** — many classes for large grammars; parser generators are preferable
- **Interpreter can be slow** — recursive object traversal incurs overhead vs. compiled alternatives
- **Visitor can separate concerns** — multiple interpretations (eval, pretty-print, optimize) can be added without touching expression classes

## OOP shape

```
interface Expression {
  interpret(context: Context): Value
}

class NumberLiteral implements Expression {
  constructor(private value: number) {}
  interpret(_ctx: Context): Value { return this.value }
}

class VariableExpression implements Expression {
  constructor(private name: string) {}
  interpret(ctx: Context): Value { return ctx.lookup(this.name) }
}

class AddExpression implements Expression {
  constructor(
    private left: Expression,
    private right: Expression
  ) {}
  interpret(ctx: Context): Value {
    return this.left.interpret(ctx) + this.right.interpret(ctx)
  }
}
```

## FP shape

```
// Expressions as algebraic data types (discriminated union)
type Expr =
  | { kind: "lit"; value: number }
  | { kind: "var"; name: string }
  | { kind: "add"; left: Expr; right: Expr }
  | { kind: "mul"; left: Expr; right: Expr }

type Context = Record<string, number>

// Interpreter is a single recursive function — pattern match on kind
const interpret = (expr: Expr, ctx: Context): number => {
  switch (expr.kind) {
    case "lit": return expr.value
    case "var": return ctx[expr.name]
    case "add": return interpret(expr.left, ctx) + interpret(expr.right, ctx)
    case "mul": return interpret(expr.left, ctx) * interpret(expr.right, ctx)
  }
}

// Multiple interpretations (eval, pretty-print) are just additional functions
// over the same Expr type — no class hierarchy modification needed
```

## Smells fixed

- **long-conditional-chain** — a deeply nested `if/else` parsing expressions is replaced by a class per rule, each handling only its own case
- **switch-on-type** — `switch (node.type)` dispatching across grammar nodes collapses into polymorphic interpret calls
- **duplicate-algorithm-variants** — similar evaluation logic duplicated across callers is consolidated inside expression classes

## Tests implied

- **Terminal determinism** — a terminal expression given the same context always returns the same value; verify with multiple identical calls
- **Composite delegation** — a non-terminal expression's interpret result equals the combination of its children's results per the grammar rule; no extra logic
- **Context isolation** — interpreting a read-only expression leaves context bindings unchanged; verify before/after state equality
- **Grammar consistency** — identical input sentences parsed and interpreted via different root compositions yield the same result

## Sources

- https://en.wikipedia.org/wiki/Interpreter_pattern
- https://www.amazon.com/Design-Patterns-Elements-Reusable-Object-Oriented/dp/0201633612
