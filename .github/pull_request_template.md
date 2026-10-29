## Pull Request Description

### Summary of Changes
- Briefly describe the purpose of this PR and what changes have been made to the agent system or tools.

---

### Type of Change
- [ ] New Agent capability / tool
- [ ] Refactor of pipeline coordination / state machine
- [ ] Statistical calculation or normalization fix
- [ ] Safety guardrail / Human-in-the-Loop enhancement
- [ ] Documentation update (`README.md`, `AGENTS.md`, or architecture)
- [ ] Test coverage expansion

---

### Agent System & Safety Checklist
- [ ] **Rubric & Design Alignment:** Changes adhere to the architecture in `AGENTS.md`.
- [ ] **Human Checkpoint:** Outlier divergence or high-uncertainty scenarios still trigger human verification.
- [ ] **No Secrets:** No real API keys, credentials, or `.env` files are added or exposed.
- [ ] **Clean Code & Typing:** Type hints and docstrings are provided.
- [ ] **Tests Pass:** All tests pass locally (`pytest -v`).
