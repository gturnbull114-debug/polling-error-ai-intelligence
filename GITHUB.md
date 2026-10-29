# GitHub & Version Control Guide — LIAI 1001

This guide explains how to initialize, manage, and push this repository to GitHub, fulfilling all version control requirements in Section 5 of the **LIAI 1001 Agentic AI Assignment**.

---

## 1. Assignment Git & GitHub Requirements

As outlined in the course rubric:
1. **Initialize Git at the start:** Maintain a clean `.git/` directory showing project evolution.
2. **At least 5 descriptive commits:** Document incremental stages of development (initial scaffold, agent cards, mathematical tools, pipeline orchestrator, human checkpoint, tests).
3. **Proper `.gitignore`:** Exclude all secrets (`.env`), virtual environments (`.venv/`), and heavy build caches.
4. **Preserve `.git/` in submission:** When preparing the final `03_Antigravity_Project` folder in your submission zip, keep the `.git/` folder intact.
5. **GitHub Link (Optional but Recommended):** You can link your private or public GitHub repository in the `README.md` and share access with Prof. Evandro Barros.

---

## 2. Step-by-Step Git & GitHub Setup

### Step 2.1: Verify or Install Git
If Git is not yet installed in your PowerShell terminal, install it quickly via Windows Package Manager (`winget`):

```powershell
winget install --id Git.Git -e --source winget
```
*(After installation finishes, close and reopen your PowerShell terminal to update your PATH).*

Verify installation:
```powershell
git --version
```

### Step 2.2: Configure Git User Info
Ensure your name and Georgian College student email are configured:
```powershell
git config --global user.name "Graham Turnbull"
git config --global user.email "your_georgian_email@student.georgiancollege.ca"
```

### Step 2.3: Initialize the Local Repository
From the root workspace directory (`c:\Users\gturn\OneDrive\Assignement LIAI 1001`):

```powershell
git init -b main
```

---

## 3. Recommended 5-Stage Commit Progression

To achieve full marks on the Git history rubric criterion, commit your progress in logical steps with descriptive messages:

### Commit 1: Initial Repository Scaffold & Architecture Guidelines
```powershell
git add .gitignore .env.example student_info.txt AGENTS.md README.md GITHUB.md .github/
git commit -m "chore(init): initialize LIAI 1001 repository scaffold with AGENTS.md, README, and GitHub CI"
```

### Commit 2: Core Data Models & Mathematical Tooling
```powershell
git add src/tools/ requirements.txt
git commit -m "feat(tools): add Bayesian consensus weighting and margin of error decomposition utilities"
```

### Commit 3: Ingestion, Modeling, and Explainer Agent Implementation
```powershell
git add src/agents/
git commit -m "feat(agents): implement NormalizerAgent, ModelerAgent, and ExplainerAgent roster"
```

### Commit 4: Orchestrator Pipeline with Human-in-the-Loop Checkpoint
```powershell
git add src/orchestrator/
git commit -m "feat(orchestrator): add pipeline state coordinator with interactive human checkpoint gate"
```

### Commit 5: Test Suite, Documentation & Evidence Artifacts
```powershell
git add tests/ docs/ evidence/
git commit -m "test(pipeline): add end-to-end integration tests and sample polling input fixtures"
```

Check your commit history anytime:
```powershell
git log --oneline --graph --decorate
```

---

## 4. Connecting to a Remote GitHub Repository

### Step 4.1: Create a Repository on GitHub
1. Log in to your GitHub account: [https://github.com](https://github.com).
2. Click **New Repository** (or visit `https://github.com/new`).
3. Repository name: `LIAI-1001-Agentic-AI-Solution`.
4. Visibility: Select **Private** (recommended for academic assignments) or **Public**.
5. Do **NOT** initialize with a README, .gitignore, or license (these already exist in this folder).
6. Click **Create repository**.

### Step 4.2: Link Local Repo to GitHub
Run the following in PowerShell (replace `YOUR_GITHUB_USERNAME` with your actual username):

```powershell
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/LIAI-1001-Agentic-AI-Solution.git
git branch -M main
git push -u origin main
```

### Step 4.3: Granting Access to the Instructor
If your repository is **Private**, grant access to Prof. Evandro Barros:
1. Go to your repository on GitHub.
2. Click **Settings** $\rightarrow$ **Collaborators**.
3. Click **Add people** and enter the instructor's GitHub username or email.

---

## 5. Security & Safety Checklist

- [x] `.env` is listed in `.gitignore` and **never** pushed to GitHub.
- [x] Only `.env.example` with mock/placeholder values is tracked.
- [x] No student passwords or confidential demographic datasets are committed.
- [x] `.git/` folder is preserved when packaging the assignment submission zip.
