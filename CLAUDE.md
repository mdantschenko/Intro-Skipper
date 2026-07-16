# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes and optimize API token usage. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:
* State your assumptions explicitly. If uncertain, ask.
* If multiple interpretations exist, present them - don't pick silently.
* If a simpler approach exists, say so. Push back when warranted.
* If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

* No features beyond what was asked.
* No abstractions for single-use code.
* No "flexibility" or "configurability" that wasn't requested.
* No error handling for impossible scenarios.
* If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:
* Don't "improve" adjacent code, comments, or formatting.
* Don't refactor things that aren't broken.
* Match existing style, even if you'd do it differently.
* If you notice unrelated dead code, mention it - don't delete it.
* **Important (iOS/Swift):** Ensure you do NOT use any code or APIs deprecated in iOS 26.0 or later (e.g., do not use `UIScreen.main`. Instead, use a `UIScreen` instance found through context like `view.window.windowScene.screen`, or use a `traitCollection` for properties like `UIScreen.scale`).

When your changes create orphans:
* Remove imports/variables/functions that YOUR changes made unused.
* Don't remove pre-existing dead code unless asked.

**The test:** Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:
* "Add validation" → "Write tests for invalid inputs, then make them pass"
* "Fix the bug" → "Write a test that reproduces it, then make it pass"
* "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
1. `[Step]` → verify: `[check]`
2. `[Step]` → verify: `[check]`
3. `[Step]` → verify: `[check]`

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. API & Token Efficiency

To prevent VS Code API rate limits, timeouts, and context exhaustion:
* **Be concise:** Output only the necessary code or brief explanations. Avoid conversational filler or repeating existing code blocks in your responses.
* **Batch file operations:** Do not read or write files one by one if they can be handled together, but avoid reading entire directories recursively.
* **Stop on continuous errors:** If a command, build, or test fails 2 times in a row with the same error, **STOP immediately**. Do not blindly retry or loop. Present the error to the user and ask for guidance.
* **Minimize context:** Only inspect files directly relevant to the current task. Do not open unrelated files "just to check".
* **No large diffs:** If a change requires modifying more than 3-4 files or hundreds of lines, pause and ask the user if the plan should be split into smaller, separate chat sessions.

---

# Python Coding Standards (MANDATORY)

Extracted from internal training ("Introduction to Python", "OOP in Python", R. Tryniecki 2025). These rules are strict — apply to ALL Python code in this project.

## 6. Style & Naming (PEP 8)

* Follow **PEP 8**. Format all code with **Black**.
* Classes: `CapWords`. Functions, methods, variables: `snake_case`.
* **No abbreviations** in names (`cashflow_calculator`, not `cf_calc`).
* Prioritize **readability over shortness/cleverness** — code must read like language sentences. Exception: deliberate, significant optimization (document why).
* **Always use type hints** on all function/method signatures and return types.
* Use `if __name__ == "__main__":` to guard script entry points.
* Use dunder methods (`__init__`, `__str__`, `__len__`, `__add__`) to define standard object behavior instead of custom ad-hoc methods.

## 7. Functions & Variables

* **Max ~60 lines per function** (NASA Power of 10, Rule 4). Split anything longer.
* **NEVER use global variables.** Pass values explicitly as parameters; return results with `return`. Module-level mutable state is forbidden.
* All constants (paths, directories, column names, magic values) live in a **separate file, grouped in their own classes** (e.g., `src/helpers/constants.py`).

## 8. OOP & SOLID

Every class/method/function must satisfy:

* **SRP (Single Responsibility):** one job, one reason to change. A `cashflow_calculator` calculates cashflows — it does NOT transform input or write PDFs. Split persistence from domain (e.g., `Person` vs `PersonDB`).
* **Open/Closed:** extend via new subclasses of an abstract base, never by modifying existing classes (e.g., new storage format = new subclass of abstract `PersonStorage`, not a new method on it).
* **Liskov Substitution:** subclasses must be drop-in replacements — never change a method's signature in a child; never use `isinstance` checks to branch on subclass type. Move subtype-specific data into `__init__`.
* **Interface Segregation:** small, cohesive interfaces. No class may be forced to implement methods it doesn't use (split `Vehicle` into `Movable` / `Flyable`).
* **Dependency Inversion:** high-level modules depend on abstractions (ABCs), not concrete classes. Inject dependencies via `__init__`; prefer the `dependency_injector` package for wiring and testability.

Core OOP rules:
* **Encapsulation:** keep internal state private (`_underscore` prefix); expose only what's necessary via methods.
* **Abstraction:** hide multi-step internals behind one simple method — callers must not need to know the call order.
* **Inheritance:** share common structure via base classes to avoid duplication.
* **Polymorphism:** one interface, type-specific behavior — no type-checking conditionals.

## 9. Pandas Best Practices

* **Never append rows in a loop.** Collect data in lists, then build the DataFrame once (~500× faster at 10k rows).
* **Always check and specify column dtypes:** `df['Age'] = df['Age'].astype('int32')`.
* **No chained indexing** (returns a copy, not a view):
  * ✅ `df.loc[df['Age'] > 25, 'Salary'] = 70000`
  * ❌ `df[df['Age'] > 25]['Salary'] = 70000`
* Use `df.loc[...]` (label-based) and `df.iloc[...]` (position-based) — never bare chained `[][]`.
* **Vectorize** operations (`df['TaxedSalary'] = df['Salary'] * 0.8`) — no row-wise loops/`apply` where vectorization works.
* Use `df.copy()` when deriving a DataFrame to avoid mutating the original.
* Filter with boolean masks: `df[df['Age'] > 25]`.

## 10. Project Structure

```
main.py (or app.py)      # single entry point — only calls classes/functions
src/                     # core logic, split by concern (loading, transform, output)
src/helpers/             # constants.py, enums.py, dtos.py
tests/                   # separated: unit/, functional/, integration/
```

* Frontend and backend live in **separate folders**.
* **Delete unused files and dead code immediately** — "if it's not in the core, throw it out the door."

## 11. Environment & Git Workflow

* Always use a **virtual environment** — prefer **uv** (`uv init`, `uv add <pkg>`, `uv sync` on a cloned repo). Never install into system Python.
* Use git for everything. `main`/`master`/`development` is **protected** — no direct or force pushes.
* All changes via **pull requests**, ≥1 approval, kept **small** (smaller beats bigger).
* Branch naming: `feature/feature-name` or `bugfix/bugfix-name`.

---
*These guidelines are working if: fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.*