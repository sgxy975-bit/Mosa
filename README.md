# Mosa

**Find Your Talent. Piece by Piece.**

> **Mosa (Multi-modal Omnichannel Skills Agent)** is a proof-of-skill platform for university clubs and student developers. It checks that a submitted GitHub project is real, interviews the person who built it with AI, and turns what they show into verified skills that collaborators can trust.

[![Gemini](https://img.shields.io/badge/Google-Gemini%203.8%20Flash-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![MongoDB Atlas](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb)](https://www.mongodb.com/atlas)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)

<img width="694" height="637" alt="Mosa人才拼图图标设计 (1)" src="https://github.com/user-attachments/assets/8991087b-ae64-46e1-89e3-4eff7b1685e8" />


**Live demo:** `[https://<your-username>.github.io/<repo-name>/](https://sgxy975-bit.github.io/Mosa/)`. It runs in the browser with no backend.

---

## 🎯 The problem

- **Target user:** **Alex**, a tech lead and open-source community manager, and the students who want to join Alex's team.
- **The problem:** Now that AI coding assistants are everywhere, GitHub portfolios are full of code the submitter may not understand. Star counts and static analysis can't show whether someone actually built and understands their project.
- **Mosa's answer:**
  1. **Scan the repository.** Read the public repo's metadata, file tree, languages and commit history to confirm it is real, active work.
  2. **Run an AI interview.** Gemini writes questions about *this* repository, mixing multiple choice and short answers, and grades the answers.
  3. **Issue verified skills.** Only skills backed by both the code and the interview are shown.
  4. **Match collaborators.** Students who opt in are matched on verified skills, not on what they claim.

---

## 📱 How it works

| Step | What happens |
| :--- | :--- |
| **1 · Submit & scan** | Paste a public GitHub URL. A four-phase scan agent validates the repo, maps its architecture (donut chart and directory tree), detects the tech stack, and reads activity (7, 30 or 90-day filter and branch selector). When the scan reaches **Ready**, the interview unlocks. |
| **2 · AI interview** | Five questions generated from the repository (3 short answer, 2 multiple choice). You can move back and forth between questions freely. |
| **3 · Report & skills** | Evidence checks, an interview score and readiness, plus a list of verified skills. |
| **Find Collaborators** | Join matching, browse students with complementary verified skills, and request an introduction. |

---

## 🛠️ Tech stack

| Part | Technology | Role |
| :--- | :--- | :--- |
| Frontend | Single-file HTML/CSS/JS, WebGL fluid intro | Runs anywhere, including GitHub Pages. Reads GitHub directly when there is no backend. |
| Backend | Python, FastAPI | Scan, verification, interview, skills and matching APIs |
| AI | Google Gemini (`gemini-3.8-flash`, JSON mode) | Writes repository-specific questions and grades answers. Built-in rules are used when no key is set. |
| Data | MongoDB Atlas | Stores projects, verifications and interview results. Falls back to in-memory storage when no database is set. |
| Source data | GitHub REST API | Repository, tree, languages, commits, contributors, branches |

---

## 🚀 Quick start

### Option A: frontend only (no setup)

Open `index.html` in a browser, or use the GitHub Pages link above.
- The example repositories (`octo-club/...`) use built-in demo data.
- Any other public repository is read live from GitHub in the browser.
- Anonymous GitHub access allows 60 requests an hour. You can add a token under **Mock Data → API settings**; it is kept for the current tab only.

### Option B: with the backend (Gemini + MongoDB)

Requires Python 3.11+.

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>/backend

python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # then fill in your keys
uvicorn main:app --reload --port 8000
```

Check `http://localhost:8000/api/health`. It reports whether the database, Gemini and the GitHub token are ready.

Connect the frontend in either of two ways:
- **Mock Data → API settings → Live API**, then enter the backend URL.
- Open `index.html?api=https://your-backend-url`. This is the easiest way to share a working link.

> `localhost` only points to the computer that opens the page. Before others can use your backend, deploy it publicly (Render, Railway, Fly.io…) or use a tunnel (`cloudflared tunnel --url http://localhost:8000`). If the frontend is served over https, the backend must be https too.

### Environment variables (`backend/.env`)

| Variable | Required | Notes |
| :--- | :--- | :--- |
| `MONGODB_ATLAS_URI` | Optional | Without it, data is kept in memory and cleared on restart |
| `GEMINI_API_KEY` | Optional | Without it, questions and grading use built-in rules |
| `GEMINI_MODEL` | Optional | Defaults to `gemini-3.8-flash`. If a model is retired for your account, the backend switches to the one Google suggests |
| `GITHUB_TOKEN` | Recommended | Raises the GitHub limit from 60 to 5,000 requests an hour |

`.env` is listed in `.gitignore`. **Never commit it.**

---

## 📁 Project structure

```
index.html              Frontend (single file)
backend/main.py         FastAPI backend
backend/requirements.txt
backend/.env.example    Environment variable template
docs/CHANGES.md         Notes on backend API changes
FLUID-LICENSE.txt       Licence for the WebGL fluid intro
```

---

## 🧭 Roadmap

These ideas are planned but **not built yet**:

- 🧪 **Sandbox execution**: run the project's tests in an isolated Linux sandbox to get real pass/fail signals.
- 🧠 **Whole-repository context**: send full code, dependency graphs and test logs to a long-context model for deeper "anti-copilot" questions.
- 🎙️ **Voice interview**: real-time spoken technical Q&A.
- 🔎 **Vector matching**: MongoDB Atlas Vector Search over skill profiles for collaborator matching.
- 🏅 **3D skill badges**: interactive WebGPU medals for verified skills.

---

## 🙏 Credits

The intro animation is adapted from [WebGL Fluid Simulation](https://github.com/PavelDoGreat/WebGL-Fluid-Simulation) by Pavel Dobryakov (MIT License). See `FLUID-LICENSE.txt`.
