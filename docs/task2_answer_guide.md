# Task 2 Answer Guide: Develop Secure Application

This guide is based on your assignment brief, README, docs, and current Flask codebase. It is written to help you produce the Task 2 section of the Word report, not to replace it. Use this as the structure for your final write-up.

## 1. What Task 2 Actually Requires

Task 2 is worth 50 marks and asks you to design, build, deploy, and test a secure application using an appropriate environment, languages, tools, and database.

Your report section for Task 2 needs to show five things clearly:

1. A brief summary and explanation of the application.
2. Evidence of your SDLC approach, at minimum planning, design, development, and testing.
3. Evidence of secure coding and discussion of at least three OWASP-related protections.
4. Evidence that the project is in an online repository and deployed live.
5. Evidence that the application stores, retrieves, updates, and deletes data correctly.

The rubric also rewards modularisation, validation, usability, refactoring, storage/retrieval, and error handling. Your current codebase already gives you strong evidence for most of that, so the main job is presenting it in a structured way.

## 2. Recommended Structure For Your Task 2 Write-Up

Use the following section structure inside your Word document.

### 2.1 Application Summary

Write one short paragraph explaining the purpose of the system.

Suggested angle:

The Internal Tool Directory is a secure Flask web application that replaces spreadsheet-based tracking of internal tools with a centralised database-backed system. It allows users to browse tools and administrators to create, edit, and archive records. The system uses Flask, SQLAlchemy 2.0, WTForms, Flask-Login, and a database that can run locally on SQLite or in production on Neon PostgreSQL.

Do not place a code snippet here. This section should stay high level.

### 2.2 Planning And Design

This section should explain how you planned the application before or during implementation.

You can cover:

- the problem being solved: replacing spreadsheet-based tool tracking
- the key user roles: standard user and admin
- the core entities: User, Team, Category, Language, Tool
- the main functional requirements: browse, add, update, delete, validation, security
- the technical design decisions: Flask app factory, modular routes, ORM, hosted database

You already have supporting material in the design docs and code structure. You can mention that the schema was normalised through separate reference tables for teams, categories, and languages.

Place one short code snippet here.

Code snippet placement:

- Insert a short model snippet after the paragraph describing the data model.
- Best source: `models.py`
- Best evidence to show: the `Tool` model and one or two foreign keys, or a `User` field plus relationship structure.

What the snippet proves:

- the application uses a real relational schema
- primary keys and foreign keys exist
- several data types are used
- the design is modular and not a single flat table

### 2.3 Development Approach And Implementation

This should be the largest part of Task 2. Split it into small sub-sections.

#### 2.3.1 Application Architecture

Explain that the application is modularised into separate files:

- `app.py` for configuration and bootstrapping
- `models.py` for database models
- `forms.py` for validation
- `routes/auth.py` for authentication and RBAC
- `routes/admin.py` for protected CRUD
- `routes/main.py` for public browsing and search
- `seed.py` for database setup and test data
- `tests/` for automated verification

Place a code snippet here only if you want to show the application factory.

Recommended snippet:

- `app.py` showing the Flask config and `SQLALCHEMY_DATABASE_URI` handling

What it proves:

- environment-aware configuration
- modular setup
- live deployment readiness

#### 2.3.2 Authentication And Password Security

Explain that the application uses Flask-Login for session-based authentication and Werkzeug hashing for password security. State clearly that passwords are never stored in plaintext.

Place a code snippet immediately after this explanation.

Recommended snippet:

- `models.py` showing `set_password()` and `check_password()`

What it proves:

- protection against OWASP A02: Cryptographic Failures
- secure credential handling

Then add one sentence linking this to testing.

Example discussion point:

This security control was verified through automated tests that confirm the stored password hash differs from the raw password and that only valid credentials are accepted.

#### 2.3.3 Role-Based Access Control

Explain that administrator routes are protected by a custom `@admin_required` decorator. Standard users and anonymous users are blocked from admin pages such as add, edit, and delete.

Place a code snippet immediately after this paragraph.

Recommended snippet:

- `routes/auth.py` showing `admin_required()`

What it proves:

- defence against OWASP A01 or A05 style broken access control issues
- explicit logging and 403 blocking behaviour

Then refer to the visible 403 security page and your test evidence.

You can mention that the application renders an explicit security alert page and logs blocked access attempts, which is stronger evidence than a generic failure page.

#### 2.3.4 Validation And Safe Data Entry

Explain that WTForms is used for server-side validation of input fields. Point out required fields, length rules, and URL validation.

Place a code snippet here.

Recommended snippet:

- `forms.py` showing `ToolForm`

What it proves:

- invalid input is constrained before database writes
- the app follows the brief requirement for validation and error prevention

Then explain that validated data is passed into the admin CRUD routes, rather than being directly interpolated into SQL strings.

#### 2.3.5 CRUD Operations And Data Management

Explain that administrators can create, edit, and archive tools, while normal users can browse them. Also explain that delete is implemented as a soft delete using the `is_active` flag.

Place one code snippet after the explanation of CRUD.

Recommended snippet:

- `routes/admin.py` showing `add_tool()` and `delete_tool()` or `_assign_tool_fields()` plus one route

What it proves:

- create, update, and delete requirements are met
- data is stored centrally in the database
- the system uses soft-delete rather than destructive removal during normal application use

Good discussion points:

- soft delete reduces accidental data loss
- flash messages improve usability
- shared helper functions reduce duplication

#### 2.3.6 Data Retrieval, Search, And Pagination

Explain how users browse records from the database. Mention that the public directory retrieves active tools only, supports search, and limits page size to 20 results.

Place a code snippet after this explanation.

Recommended snippet:

- `routes/main.py` showing `_build_directory_statement()` and the `limit(PAGE_SIZE + 1)` pagination logic

What it proves:

- centralised data retrieval
- efficient querying
- storage and retrieval requirements are met
- SQLAlchemy 2.0 ORM is used instead of raw SQL

This is also a good place to mention that eager loading via `joinedload()` avoids inefficient repeated queries when rendering related data.

### 2.4 SDLC Approach

The brief explicitly wants planning, design, develop, and testing. A clean way to answer this is with four short sub-headings.

#### Planning

Discuss the business problem, user roles, core features, and security requirements.

Evidence you can reference:

- README overview
- technical design document
- route and model structure

No code snippet needed.

#### Design

Discuss the entity structure, modular file organisation, and technology choices.

Optional code snippet placement:

- if you did not already use a model snippet in section 2.2, place it here instead

#### Develop

Discuss incremental implementation of authentication, admin CRUD, search, pagination, and deployment configuration.

Best snippet placement:

- use the admin CRUD or directory query snippet here if you prefer the SDLC narrative to be code-led

#### Testing

Explain that testing was automated using Pytest and that the codebase contains slice-based tests plus OWASP-focused tests.

Place a code snippet here.

Recommended snippet:

- `tests/test_security_owasp.py` showing blocked admin access or SQL injection search test
- or `tests/test_slice2_auth.py` showing password hashing verification

What it proves:

- secure behaviour was tested, not just claimed
- the development process followed a disciplined feedback loop

### 2.5 OWASP Security Discussion

This part is essential because the brief explicitly asks for screenshots or video of the app defending itself from at least three different OWASP Top 10 vulnerabilities.

Your safest three to discuss from the current codebase are:

#### 1. Broken Access Control

Evidence:

- protected admin routes in `routes/auth.py`
- blocked responses verified in `tests/test_security_owasp.py`
- visible security alert page in `templates/errors/403.html`

What to say:

Unauthenticated and non-admin users are prevented from accessing privileged routes such as `/admin`, `/admin/add`, `/admin/edit/<id>`, and `/admin/delete/<id>`. The app logs the attempt and returns an explicit 403 security page.

Screenshot/video evidence to include:

- attempt to open an admin URL as a normal user
- resulting 403 page with the security alert message

#### 2. Injection

Evidence:

- SQLAlchemy ORM queries in `routes/main.py`, `routes/admin.py`, and `routes/auth.py`
- validation in `forms.py`
- security test for SQL injection payload in `tests/test_security_owasp.py`

What to say:

The app does not use raw SQL. Queries are built through SQLAlchemy ORM expressions, which prevents unsafe string concatenation. This was tested using a classic SQL injection payload in the search route, and no records were exposed.

Screenshot/video evidence to include:

- submit `' OR 1=1 --` in the search input
- show that matching records are not dumped and the page remains safe

#### 3. Cryptographic Failures

Evidence:

- password hashing in `models.py`
- login verification in `routes/auth.py`
- password hashing test in `tests/test_slice2_auth.py`

What to say:

Passwords are hashed using Werkzeug before storage, and user login checks the hash instead of storing or comparing plaintext credentials directly.

Screenshot/video evidence to include:

- optional database screenshot showing hashed passwords rather than readable values
- or show the relevant unit test and explain what it proves

Important note:

Do not claim protections you have not actually implemented and tested. Stay with the three above unless you add more evidence first.

### 2.6 Deployment And Repository Evidence

The brief also requires a repository and a live deployment link.

Include a short paragraph explaining that:

- the source code is version controlled in GitHub
- CI runs automated tests using GitHub Actions
- the app is deployed online using Render
- production data is hosted on Neon PostgreSQL through `DATABASE_URL`

Place one short code/config snippet here.

Recommended snippet:

- `.github/workflows/ci.yml` showing the test job, database service, and `pytest`
- `render.yaml` showing the build and start commands

What it proves:

- the project is not just local code
- the application is tested and deployed through a DevOps-style workflow

Then paste your actual links under the paragraph:

- GitHub repository link
- live Render link

### 2.7 Closing Evaluation Paragraph

End Task 2 with a short evaluative paragraph, not just a summary.

Suggested angle:

The final solution meets the brief by providing a secure, modular, database-backed web application with authentication, RBAC-protected CRUD, validation, centralised data storage, automated testing, and live deployment. The strongest aspects are secure access control, ORM-based data handling, and test coverage. A reasonable future improvement would be expanding audit logging or adding finer-grained security monitoring.

## 3. Best Places To Insert Code Snippets

Use short code snippets, not full files. Each snippet should usually be around 8 to 20 lines and followed by a short explanation of what it proves.

Recommended order:

1. Data model snippet after the planning/design section.
2. Password hashing snippet after the authentication paragraph.
3. `@admin_required` snippet after the broken access control paragraph.
4. WTForms validation snippet after the validation paragraph.
5. CRUD route snippet after the create/update/delete paragraph.
6. Query and pagination snippet after the storage/retrieval paragraph.
7. Test snippet after the testing section.
8. CI/CD config snippet near the deployment evidence section.

Avoid placing all snippets together at the end. Spread them throughout the narrative exactly where they support the discussion.

## 4. Strong Snippet Sources In This Codebase

Use these files as your primary sources:

- `models.py` for schema, password hashing, and admin role checks
- `forms.py` for validation rules
- `routes/auth.py` for authentication and RBAC
- `routes/admin.py` for CRUD implementation
- `routes/main.py` for retrieval, search, and pagination
- `tests/test_security_owasp.py` for security testing evidence
- `tests/test_slice2_auth.py` for password hashing verification
- `.github/workflows/ci.yml` for automated test evidence
- `render.yaml` for deployment evidence

## 5. Suggested Evidence Checklist For Task 2

Before you finalise the report, make sure Task 2 includes:

- a brief application summary
- planning, design, develop, and testing discussion
- at least one repository link
- one live deployment link
- screenshots of the app running
- screenshots or short video evidence of three OWASP protections
- code snippets placed inside the relevant paragraphs
- a short explanation after every snippet
- brief evaluation, not just description

## 6. What To Avoid

- do not paste entire files into the report
- do not describe the app only from a user perspective; link features to code
- do not list OWASP items without showing where your code defends against them
- do not say the app uses raw SQL, because it does not
- do not claim full production security maturity; keep your evaluation realistic

## 7. Quick Writing Formula For Each Paragraph

For most Task 2 paragraphs, use this pattern:

1. State the feature or engineering decision.
2. Explain how it works in your application.
3. Show the supporting code snippet or screenshot.
4. Evaluate why it matters for security, usability, or maintainability.

If you follow that structure consistently, your Task 2 section will read like an analysis rather than a feature list.