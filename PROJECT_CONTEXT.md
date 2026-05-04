# **📝 Product Requirements Document (PRD): Internal Tool Directory**

## **1. Problem Statement**

The organization currently relies on a static, difficult-to-maintain spreadsheet to track internal tools, and their respective data sources. This makes it hard for employees to discover what resources are available, who created them, and where to find the underlying data. Furthermore, the spreadsheet lacks proper access control, data validation, and a user-friendly interface.

## **2. The Solution**

We will build a secure, centralized web application to replace the spreadsheet. Built using Python, Flask, and SQLAlchemy, the application will provide a read-only dashboard for standard users to search and discover tools. It will also feature a secure, Role-Based Access Control (RBAC) administrator portal where authorised users can perform CRUD (Create, Read, Update, Delete) operations to keep the directory updated.

## **3. Architectural Boundaries & Constraints**

Based on senior engineering and DevOps review, the following boundaries are **strictly enforced** to align with project requirements while avoiding over-engineering:

  - **Data Modeling:** A single Tool database table will handle internal tools  to maintain clean, simple CRUD operations.
  - **Authentication:** Local authentication using Flask-Login and Werkzeug password hashing. Admins manually create users. **No SSO or self-service registration.**
  - **Legacy Data:** Migration of the legacy spreadsheet is out of scope for the MVP. The database will start blank, populated purely by Python seed scripts during development and testing.
  - **Search UX:** Search results enforce a hard backend limit (e.g., .limit(20)) to guarantee a clean, professional UI, completely avoiding pagination overhead.
  - **Initial Query:** stmt = select(Tool).limit(21) (fetching 21 items to see if a "next page" exists).
      - **Logic:** Fetching 21 items allows the system to check if a "next page" exists without a heavy COUNT query.
      - **UI/UX:**

<!-- end list -->

  - Display the first 20 results.
  - If a 21st item exists, display a **"Load More"** button at the bottom of the list.
  - Ensure the .ilike() search allows users to eventually see all matching records via the "Load More" functionality.
  - Avoid complex numbered pagination overhead to keep the UI clean.

<!-- end list -->

  - **Soft Deletes:** Use an is\_active boolean for tools instead of hard deletion to prevent accidental data loss.
  - **Security:** \* **No Raw SQL:** All interactions must use SQLAlchemy ORM to prevent SQL Injection (OWASP 2017 \#A1: Injection).
  - **RBAC:** Use a custom @admin\_required decorator to protect administrative routes (OWASP 2017 \#A5: Broken Access Control).
  - **Validation:** Use WTForms for all backend data validation, specifically for dropdown menus.

## **4. User Stories**

  - **Authentication:** As a user, I want to securely register and log in so that my access level (Standard or Admin) can be verified.
  - **Discovery:** As a standard user, I want to view a dashboard of all available tools and search by name or category, so that I can easily find resources for my work.
  - **Access:** As a standard user, I want to view detailed information about a tool and click a link to access its underlying data source.
  - **Management:** As an administrator, I want to access a protected /admin dashboard so that I can manage the directory.
  - **Data Entry:** As an administrator, I want to use forms with dropdown menus (for Categories, Teams, Languages) to add, edit, or delete tools, so that data entry is standardized and prevents typos.

## **5. Implementation Decisions**

  - **Framework & Architecture:** Python with Flask. We will use Jinja2 for server-side HTML rendering to explicitly demonstrate Model-View-Controller (MVC) architecture.
  - **Database & ORM (Deep Module):** SQLite managed via Flask-SQLAlchemy for local development. **Crucial Security Constraint:** All database interactions MUST use SQLAlchemy's ORM to ensure parameterized queries, acting as our explicit defense against OWASP 2017 \#A1: Injection. Raw SQL is strictly forbidden.
  - **Security & Interfaces:**
      - **OWASP 2017 \#A5 (Broken Access Control):** We will design a custom @admin\_required decorator interface. This will wrap all CRUD routes (e.g., /admin/add) to intercept standard users and return a 401/403 or redirect them.
      - **OWASP 2017 \#A3 (Sensitive Data Exposure/Cryptographic Failures):** We will use werkzeug.security (generate\_password\_hash and check\_password\_hash). Passwords must be hashed instantly upon registration.
  - **Data Models (SQLAlchemy Definitions):**
      - User: id (PK), username (Unique), password\_hash, is\_admin (Boolean).
      - Tool: id (PK), name, description, data\_link, creator, category, language.

## **6. Out of Scope**

  - Single Sign-On (SSO) or OAuth integration.
  - Complex frontend Javascript frameworks (React, Vue, Angular).
  - Bulk CSV import/export functionality for administrators.

## **7. Directory structure**

```
/project\_root

├── app.py

├── models.py

├── seed.py

├── requirements.txt

├── /templates

│   ├── base.html

│   └── index.html

└── /tests

    ├── conftest.py

    ├── test\_models.py

    └── test\_routes.py
```
## **8. Dependencies Version**

**Framework Versions (CRITICAL):** \* Flask \>= 3.0

  - Flask-SQLAlchemy \>= 3.1
  - SQLAlchemy \>= 2.0 (You must strictly use 2.0-style queries, e.g., db.session.execute(select(Tool)). Do NOT use legacy Tool.query.all() syntax).
  - \# --- Core Framework & Routing ---
  - Flask\>=3.0.0
  - Werkzeug\>=3.0.0
  - 
  - \# --- Database & ORM (CRITICAL PINS) ---
  - SQLAlchemy\>=2.0.0
  - Flask-SQLAlchemy\>=3.1.0
  - 
  - \# --- Forms & Validation ---
  - Flask-WTF\>=1.2.0
  - WTForms\>=3.1.0
  - 
  - \# --- Authentication & Security ---
  - Flask-Login\>=0.6.3
  - 
  - \# --- Database Drivers ---
  - \# (PostgreSQL adapter for CI/CD; SQLite is built into Python)
  - psycopg2-binary\>=2.9.9 
  - 
  - \# --- Testing & Development ---
  - pytest\>=8.0.0
  - pytest-flask\>=1.3.0
  - 

-----

## **7. Implementation Kanban (Vertical Slices)**

**Instructions for AI Assistant:** Do not build the entire app at once. Implement this step-by-step, verifying each slice works before moving to the next.

### **Slice 1: Project Initialisation & Data Foundation**

  - **Goal:** Set up the Flask application and establish the database schema.
  - **Tasks:**
      - Initialise standard Flask project structure (app.py, models.py, /templates).
      - Configure SQLAlchemy with SQLite for local development.
      - Create the Tool and User models exactly as specified in the PRD.
      - Write a seed.py script to generate synthetic dummy data (e.g., 50 fake tools, 1 Admin user, 1 Standard user) for local development and CI/CD testing.
  - **Acceptance Criteria:** Running python seed.py creates a populated instance/app.db without errors.

### **Slice 2: Authentication & Security Layer**

  - **Goal:** Implement secure access control targeting OWASP standards.
  - **Tasks:**
      - Set up Flask-Login for session management.
      - Implement secure password hashing using Werkzeug.security.
      - Create a simple base template (base.html) with a navbar that changes based on login status.
      - Create a custom @admin\_required decorator to strictly protect admin-only routes.
  - **Acceptance Criteria:** A user can be created, their password is saved as a hash, they can log in, and they can log out.

### **Slice 3: Administrator Dashboard (CRUD)**

  - **Goal:** Allow logged-in administrators to manage the directory.
  - **Tasks:**
      - Build /admin/add, /admin/edit/\<id\>, and /admin/delete/\<id\> routes and associated templates.
      - Apply the @admin\_required decorator to **ALL** these routes.
  - **Acceptance Criteria:** Logged-in admin can create, read, update, and delete tools. Unauthenticated users attempting to access these routes receive a 401 Unauthorized or 403 Forbidden response.

### **Slice 4: User Experience (Read & Search)**

  - **Goal:** Allow standard users to find the tools they need.
  - **Tasks:**
      - Build the main / (index) dashboard displaying tools as cards or a clean table.
      - Implement a simple search bar allowing users to filter by name or category using SQLAlchemy .ilike() queries.
      - Apply .limit(20) to the query results to ensure UI stability regardless of database size.
  - **Acceptance Criteria:** Regular users can browse and search the database securely, returning a maximum of 20 results.

### **Slice 5: DevOps Packaging & CI/CD**

  - **Goal:** Fulfill the "DevOps systems development approach" and automated testing requirements.
  - **Tasks:**
      - Generate a requirements.txt file and write a Dockerfile for local containerisation (exposing port 5000).
      - Create a GitHub Actions CI pipeline (.github/workflows/ci.yml) triggered on push to main.
      - **CI Pipeline Specifications:**
          - Spin up a PostgreSQL service container within the runner.
          - Inject secure environment variables (e.g., POSTGRES\_PASSWORD) strictly via **GitHub Secrets**.
          - Run the synthetic data seed script to populate the test database.
          - Execute an automated pytest suite.
      - **Security Tests Scope (Pytest):**
          - *Authentication Defense:* Assert that unauthenticated GET/POST requests to /admin/\* routes correctly return 401/403 HTTP status codes.
          - *Injection Defense:* Assert that passing common SQL injection payloads into the search bar does not crash the application or expose unintended data records.
