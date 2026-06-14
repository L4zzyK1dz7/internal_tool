# Technical Design Document (TDD): Internal Tool Directory

## 1. System Overview & SDLC Approach
The Internal Tool Directory is a centralised, secure web application built to replace static spreadsheet tracking. The system is engineered using a strict Software Development Life Cycle (SDLC) prioritising Test-Driven Development (TDD) and a modern DevOps CI/CD pipeline.

* **Planning & Design:** Architecture defined via explicit Entity-Relationship modeling, Deep Module structural boundaries, and CALMS-aligned DevOps strategies.
* **Develop:** Python/Flask backend using strictly parameterised SQLAlchemy 2.0 ORM queries, with logic encapsulated in deep modules.
* **Testing (CI):** Automated Continuous Integration via GitHub Actions running Pytest suites on every push.
* **Deployment (CD):** Continuous Deployment hosted live on Render, backed by a persistent Neon Serverless PostgreSQL database.

---

## 2. High-Level Architecture
The application follows a multi-tier architecture, completely decoupled from its environment to allow seamless transitions from local development to cloud production.

* **Client Layer:** HTML/CSS views rendered via Jinja2 (auto-escaping enabled). Features explicit "Security Alert" visual states for OWASP defense logging.
* **Application Layer:** Flask web server handling business logic, routing, and Role-Based Access Control (RBAC).
* **Data Access Layer:** `Flask-SQLAlchemy` utilising **strict SQLAlchemy 2.0 syntax** (`db.session.execute(select(...))`).
* **CI/CD Infrastructure:** GitHub Actions (CI) acting as the testing gatekeeper, and Render (CD) executing automated build scripts (`seed.py`) against a remote PostgreSQL instance.

```mermaid
graph TD
    Client[Web Browser] -->|HTTP Request| FlaskApp[Flask Server / Render]
    
    subgraph DevOps CI/CD Pipeline
        Dev[Developer Push] --> GH[GitHub Actions / Pytest]
        GH -->|Passes Gate| RenderBuild[Render Build Phase]
        RenderBuild -->|Executes seed.py| AppState[Live Application]
    end

    subgraph Application Stack
        FlaskApp -->|Template Rendering| Views[Jinja2 / Explicit Error Views]
        FlaskApp -->|Session & RBAC| Auth[Flask-Login]
        FlaskApp -->|Security Logging| Logger[Python Logging Module]
        FlaskApp -->|Data Access| ORM[SQLAlchemy 2.0]
        ORM -->|Dynamic Connection URI| DB[(Local SQLite OR Neon PostgreSQL)]
    end
```

---

## 3. Entity-Relationship Diagram (ERD)
The schema normalises metadata (Teams, Languages, Categories) into reference tables to maintain data integrity and allow for standardised WTForms dropdowns. 

```mermaid
erDiagram
    USER {
        int id PK
        string username UK "Not Null"
        string password_hash "Not Null"
        string role "default='user'"
        int team_id FK
    }
    TEAM {
        int id PK
        string name UK
    }
    LANGUAGE {
        int id PK
        string name UK
    }
    CATEGORY {
        int id PK
        string name UK
    }
    TOOL {
        int id PK
        string name "Not Null"
        text description
        string data_link
        int creator_id FK
        int category_id FK
        int language_id FK
        datetime created_at
    }

    TEAM ||--o{ USER : "groups"
    USER ||--o{ TOOL : "creates"
    CATEGORY ||--o{ TOOL : "categorises"
    LANGUAGE ||--o{ TOOL : "built with"
```

---

## 4. Application Data Flow (With Security Defenses)
This flow depicts standard access alongside the explicit OWASP defense mechanisms required for examiner video evidence.

```mermaid
sequenceDiagram
    actor U as User
    participant UI as Browser (Client)
    participant App as Flask Application
    participant Security as RBAC & Validation Layer
    participant Log as Backend Logger
    participant ORM as SQLAlchemy 2.0

    U->>UI: Navigates to /admin/add
    UI->>App: GET /admin/add
    App->>Security: Check @admin_required
    
    alt User is NOT Admin (OWASP #A5 Defense)
        Security-->>App: Block Request
        App->>Log: Warning: Unauthorised Admin Access Attempt
        App->>UI: Render Explicit Security Alert View (403)
        UI-->>U: Displays "Security Block: Admin Rights Required"
    else User IS Admin
        Security-->>App: Allow Request
        App->>UI: Render Admin Form
        U->>UI: Submits Malicious SQL Input
        UI->>App: POST /admin/add
        App->>Security: WTForms Validation (OWASP #A1 Defense)
        Security-->>App: Sanitise & Reject Malicious Payload
        App->>ORM: Safe Parameterised DB Execution
    end
```

---

## 5. Codebase Structure & Deep Modules
The application limits exposed complexity by separating concerns into focused directories. The inclusion of CI/CD files (`.github`, `render.yaml`, `Makefile`) provides the necessary DevOps artifacts for assessment grading.

```text
/project_root
├── .github/
│   └── workflows/
│       └── ci.yml              # CI Pipeline: Pytest security suite
├── render.yaml                 # CD Pipeline: Infrastructure as Code (IaC)
├── Makefile                    # Build Automation Tool (Testing, Linting, Docker)
├── requirements.txt            # Python dependencies (incl. psycopg2-binary)
├── app.py                      # Flask application factory
├── models.py                   # SQLAlchemy 2.0 ORM models
├── forms.py                    # WTForms definitions
├── seed.py                     # Database initialisation & CI/CD synthetic data
├── routes/                     # Deep modules for business logic
│   ├── auth.py                 # Login, Registration
│   ├── admin.py                # CRUD operations + @admin_required
│   └── errors.py               # EXPLICIT Security/OWASP Violation Handlers
├── templates/                  
│   ├── base.html               
│   ├── admin/                  
│   ├── directory/              
│   └── errors/                 # Highly visible security block views for video evidence
└── tests/                      # TDD Test Suite (pytest)
    ├── conftest.py             
    ├── test_security_owasp.py  # Explicit security tests (Auth bypass, injection)
    └── test_routes.py          
```

---