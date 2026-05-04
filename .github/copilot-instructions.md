# AI Agent Instructions: Agentic Engineering Workflow

Welcome to the project. As an AI coding assistant, your goal is to practice "Agentic Engineering" rather than "vibe coding" [cite: 407, 408]. This means preserving the high quality bar of professional software, maintaining strict security, and keeping software entropy low [cite: 408, 444].

You must strictly adhere to the following architectural constraints, design philosophies, and workflows.

## 1. Core Architectural Constraints
* **Tech Stack:** Python, Flask, and SQLAlchemy [cite: 71, 98].
* **Database & ORM:** Use SQLAlchemy 2.0-style queries strictly (e.g., `db.session.execute(select(Tool))`) [cite: 129]. Legacy `Tool.query.all()` syntax is forbidden [cite: 129]. 
* **Zero Tolerance for Raw SQL:** All database interactions MUST use SQLAlchemy's ORM to ensure parameterized queries and prevent SQL Injection (OWASP #3) [cite: 88, 100]. Raw SQL is strictly forbidden [cite: 101].
* **Authentication & RBAC:** Implement local authentication with `Flask-Login` and `Werkzeug` password hashing [cite: 76, 161, 162]. Protect administrative routes strictly using a custom `@admin_required` decorator (OWASP #1 defense) [cite: 89, 103, 164].
* **Validation:** All backend data validation must use `WTForms` [cite: 90].
* **Pagination/Search Constraints:** Hardcode backend limits on searches (e.g., `.limit(20)`) to avoid heavy `COUNT` query overhead and complex numbered pagination [cite: 79, 81, 86, 178].

## 2. Software Engineering Fundamentals
Software fundamentals matter more than ever [cite: 438, 446]. Ensure all generated code adheres to the following laws of software engineering:
* **Deep Modules:** Do not create scattered, shallow modules with complex interfaces [cite: 464]. Favor "Deep Modules" that hide substantial complexity behind simple, clear interfaces [cite: 463]. The human engineer designs the interface; you (the agent) delegate the implementation details [cite: 470].
* **The Boy Scout Rule:** Leave the code better than you found it [cite: 5]. Fix broken windows (bad design, poor code) immediately [cite: 30].
* **YAGNI & KISS:** Do not add functionality until it is absolutely necessary (You Aren't Gonna Need It) [cite: 6]. Keep designs and systems as simple as possible (Keep It Simple, Stupid) [cite: 40].
* **DRY:** Every piece of knowledge must have a single, unambiguous representation [cite: 39].
* **Law of Demeter:** Objects should only interact with immediate friends, not strangers [cite: 42].

## 3. Workflow & Development Approach
* **Test-Driven Development (TDD):** The rate of feedback is your speed limit [cite: 460]. You must write failing tests first (Red), implement the code to pass them (Green), and then optimize (Refactor) [cite: 316, 460]. Wrap test boundaries around deep modules rather than tightly coupling to fragile inner functions [cite: 335, 461].
* **Vertical Slices (Tracer Bullets):** Never code horizontally (e.g., building the whole database layer, then the whole API layer) [cite: 273, 274]. Build in "vertical slices" or "tracer bullets" across the stack to guarantee rapid, visible feedback on the integrated system [cite: 271, 275, 277].
* **Feedback Loops:** Always run the test suite (`pytest`) and type checking after generating code to ensure you are not coding blind [cite: 189, 322, 458]. Fix errors automatically.
* **Maintain Context & Ubiquitous Language:** Use the same consistent terminology (ubiquitous language) in your code, variables, and comments as established in the project specs [cite: 455]. 

## 4. Execution Directives
When implementing a task or GitHub issue:
1.  **Read the PRD/Issue:** Fully understand the specific goal and constraints.
2.  **Explore the Codebase:** Navigate dependencies and locate the existing deep modules you need to interact with [cite: 208].
3.  **Implement via TDD:** Start with a test. 
4.  **Run Feedback Loops:** Execute tests and type checks [cite: 321]. Do not mark a task complete until all feedback loops pass [cite: 318, 323].
