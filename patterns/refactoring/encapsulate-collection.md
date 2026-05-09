---
name: encapsulate-collection
category: refactoring
aliases: [collection-encapsulation]
intent: >-
  Return an unmodifiable view of a collection field and provide explicit add/remove methods so the owning class controls all mutations
sources:
  - https://refactoring.guru/encapsulate-collection
  - https://refactoring.com/catalog/encapsulateCollection.html
smells_it_fixes:
  - inappropriate-intimacy
  - mutable-shared-state
  - shotgun-surgery
smells_it_introduces:
  - accessor-noise
  - copy-overhead
composes_with:
  - encapsulate-field
  - hide-delegate
  - replace-data-value-with-object
clashes_with:
  - remove-middle-man
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "external callers cannot modify the collection directly through the returned reference"
  - "every mutation to the collection routes through the owning class's add/remove methods"
---

# Encapsulate Collection

## Intent
A class exposes a mutable collection field. Any caller can add or remove elements without the owning class knowing, breaking invariants silently. Replace the raw getter with one that returns an unmodifiable view (or a copy), and add explicit `add` and `remove` methods. The class regains control over every mutation to its collection.

## Structure
```
Before:
  class Course
    prerequisites: List<Course>    ← raw mutable list exposed

  course.getPrerequisites().add(anotherCourse)    ← caller mutates directly

After:
  class Course
    private _prerequisites: List<Course>

    getPrerequisites(): ReadOnlyList<Course>    ← unmodifiable view
    addPrerequisite(c: Course): Unit
    removePrerequisite(c: Course): Unit
```

## Applicability
- A class exposes a mutable collection (list, set, map) via a getter and callers mutate it directly
- The owning class needs to enforce invariants on its collection (size limits, uniqueness, referential integrity)
- The collection is used in an observer/event pattern where additions must trigger notifications
- Defensive copying is already being done ad-hoc at call sites — centralize it

## Consequences
- **Gains**: owning class controls all mutations; invariants can be enforced; observer hooks become possible; collection can be replaced with a different implementation transparently
- **Costs**: callers must use add/remove methods instead of direct mutation; returning a copy (vs. a view) incurs allocation overhead

## OOP shape
```
class Person
  private _courses: List<Course> = []

  getCourses(): ReadOnlyList<Course>
    return unmodifiableView(_courses)    // or copy

  addCourse(c: Course): Unit
    _courses.add(c)

  removeCourse(c: Course): Unit
    if not _courses.contains(c)
      raise CourseNotFoundException
    _courses.remove(c)
```

## FP shape
```
// FP: the collection is part of the immutable record;
// "mutations" return a new record
type Person = { courses: List<Course> }

add_course(p: Person, c: Course) -> Person =
  { p | courses: p.courses ++ [c] }

remove_course(p: Person, c: Course) -> Result<Person, Error> =
  if not list_contains(p.courses, c)
    Error("course not found")
  else
    Ok({ p | courses: list_remove(p.courses, c) })

// Callers read via p.courses (immutable list)
```

## Smells fixed
- **inappropriate-intimacy**: callers no longer mutate the class's internal collection directly
- **mutable-shared-state**: all collection mutations route through the owning class, preventing silent external modification
- **shotgun-surgery**: logic that must execute on every collection change (validation, notification) is centralized in add/remove

## Tests implied
- The getter returns a read-only view — attempting to mutate it raises an error or produces no effect on the original
- Adding and removing elements through the explicit methods produces the expected collection state

## Sources
- https://refactoring.guru/encapsulate-collection
- https://refactoring.com/catalog/encapsulateCollection.html
