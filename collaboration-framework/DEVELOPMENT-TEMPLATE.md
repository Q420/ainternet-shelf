# Software Development Template

**Adopted for this project at Ben's direction, 2026-11-21 ("I'd like you guys to use this as your template"). Text as provided by Ben; the adoption mapping is at TEMPLATE-ADOPTION.md.**

A practical, reusable structure you can adapt to Agile, Scrum, Kanban, or a lightweight waterfall approach.

---

### 1. High-Level Process Overview

| Phase              | Goal                              | Key Outputs                          | Typical Duration |
|--------------------|-----------------------------------|--------------------------------------|------------------|
| Discovery & Planning | Understand problem & constraints | Vision, goals, high-level roadmap   | 1–2 weeks       |
| Requirements       | Define what to build              | User stories / PRD, acceptance criteria | 1–3 weeks     |
| Design             | Decide how to build it            | Architecture, UI/UX, data model     | 1–3 weeks       |
| Implementation     | Build the software                | Working code, PRs, documentation    | Ongoing         |
| Testing & QA       | Verify quality                    | Test plans, automated tests, bug reports | Continuous   |
| Deployment         | Release to users                  | Release notes, deployment checklist | Per release     |
| Maintenance & Ops  | Keep it running & improve         | Monitoring, incident reports, backlog | Ongoing       |

---

### 2. Recommended Project Structure (Folder Layout)

```
project-name/
├── README.md                 # Project overview, setup, contribution guide
├── docs/
│   ├── vision.md             # Product vision & goals
│   ├── requirements/         # PRD, user stories, acceptance criteria
│   ├── architecture/         # System design, ADRs, diagrams
│   ├── api/                  # API specs (OpenAPI/Swagger)
│   └── decisions/            # Architecture Decision Records (ADRs)
├── src/                      # Application source code
│   ├── frontend/             # or client/
│   ├── backend/              # or server/api/
│   ├── shared/               # Common types/utilities
│   └── ...
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
├── scripts/                  # Build, deploy, migration scripts
├── infra/                    # Infrastructure as Code (Terraform, CDK, etc.)
├── .github/ (or .gitlab/)    # CI/CD workflows
├── docker/ or Dockerfile
├── package.json / pyproject.toml / go.mod / etc.
├── .env.example
├── LICENSE
└── CONTRIBUTING.md
```

Adjust the `src/` layout to match your stack (monorepo, microservices, mobile, etc.).

---

### 3. Core Artifacts & Templates

**A. Vision / Product Brief**
- Problem statement
- Target users & personas
- Success metrics (KPIs)
- Out of scope
- High-level timeline / milestones

**B. Requirements**
- User stories in the format:
  *As a [user], I want [goal] so that [benefit].*
- Acceptance criteria (Given / When / Then or checklist)
- Non-functional requirements (performance, security, accessibility, scalability)
- Prioritization (MoSCoW or RICE)

**C. Architecture Decision Records (ADRs)**
Keep one short markdown file per significant decision:
```
# ADR-001: Choice of Database

## Status
Accepted

## Context
...

## Decision
...

## Consequences
...
```

**D. Definition of Done (DoD)**
Example checklist every story/PR should satisfy:
- [ ] Code reviewed and approved
- [ ] Unit + integration tests written and passing
- [ ] Documentation updated
- [ ] No critical linter/security issues
- [ ] Deployed to staging and verified
- [ ] Acceptance criteria met

**E. Release Checklist**
- Version bumped
- Changelog updated
- Database migrations tested
- Feature flags configured (if used)
- Monitoring & alerts verified
- Rollback plan documented

---

### 4. Lightweight Workflow (Recommended Starting Point)

1. **Backlog** → Prioritized list of user stories / issues
2. **Sprint / Iteration Planning** (1–2 weeks)
3. **Daily progress** (stand-up or async updates)
4. **Implementation** → Branch → PR → Review → Merge
5. **Continuous Integration** → Automated tests + linting on every PR
6. **Demo / Review** at end of iteration
7. **Retrospective** → What went well / improve
8. **Release** when ready (continuous or scheduled)

---

### 5. Essential Supporting Practices

- **Version control**: Git + clear branching strategy (trunk-based or GitHub Flow)
- **CI/CD**: Automated build, test, and deploy pipelines
- **Code quality**: Linters, formatters, type checking, pre-commit hooks
- **Testing strategy**: Unit → Integration → E2E + manual exploratory
- **Observability**: Logging, metrics, tracing, error tracking
- **Security**: Dependency scanning, secrets management, least privilege
- **Documentation**: Living docs in the repo (README + docs/ folder)

---

### 6. Quick-Start Checklist for a New Project

- [ ] Create repository and set up README
- [ ] Define vision and initial scope
- [ ] Choose tech stack and document key ADRs
- [ ] Set up project structure + basic CI
- [ ] Write first few user stories with acceptance criteria
- [ ] Establish Definition of Done and branching rules
- [ ] Set up staging environment and deployment pipeline
- [ ] Add basic monitoring and error tracking
