# Mosa
mosa: Find Your Talent. Piece by Piece.
# 🎖️ Mosa — Proof of Skill Agent Platform

> **MOSA (Multi-modal Omnichannel Skills Agent)** is an autonomous developer verification platform. It validates true code ownership and technical proficiency for GitHub submissions using **Gemini 4 Argon**, isolated **Antigravity Linux sandboxes**, **MongoDB Atlas Vector Search**, and **WebGPU 3D skill badges**.

[![Build with Gemini 4 Argon](https://img.shields.io/badge/Google%20DeepMind-Gemini%204%20Argon-4285F4?style=for-the-badge&logo=google)](https://deepmind.google/)
[![Powered by MongoDB Atlas](https://img.shields.io/badge/MongoDB-Atlas%20Vector%20Search-47A248?style=for-the-badge&logo=mongodb)](https://www.mongodb.com/atlas)

---

## 🎯 The Problem & Real-World Impact

* **Target User**: **Alex** (Tech Lead & Open-Source Community Manager).
* **The Problem**: In the era of LLM coding assistants, resumes and GitHub portfolios are saturated with AI-generated code. Traditional static analysis or basic RAG cannot tell if a developer **truly understands** the codebase they submitted.
* **The MOSA Solution**: 
  1. **Sandbox Autonomy**: Executes unit tests and runtime checks inside an isolated Linux sandbox to obtain concrete pass/fail signals.
  2. **Anti-Copilot Q&A Engine**: Feeds 1M tokens of codebase + test logs into **Gemini 4 Argon** to identify non-trivial architecture choices and generate targeted deep Q&A.
  3. **Multimodal Oral Defense**: Conducts real-time voice verification via **Gemini 3.8 Live**.
  4. **Proof-of-Skill On-Chain/3D Medals**: Generates dynamic WebGPU badges backed by **MongoDB Atlas** vector profile indexing.

---

## 🛠️ DeepMind Toolkit & MongoDB Integration

| Technology / Model | Role in MOSA System |
| :--- | :--- |
| **`gemini-4-argon`** | **Lead Orchestrator**: Leverages 1M token context to process full repo histories, dependency graphs, and test logs to formulate anti-copilot technical questions. |
| **`antigravity-preview-09-2026`** | **Linux Sandbox Agent**: Executes test suites and compiler checks to pass deterministic verification signals back to Argon. |
| **`gemini-3.8-live`** | **Voice Interrogator**: Powers real-time interactive audio defense during the candidate AI interview. |
| **MongoDB Atlas** | **Developer Data Platform**: Utilizes Atlas Vector Search, Hybrid Search, and Automated Embeddings to query codebase chunks and index candidate skill profiles. |

---

## 📱 Features & App Walkthrough

- 🔍 **GitHub Repository Ingestion**: Submit any repository URL or Markdown documentation for deep contextual parsing.
- 🧪 **Autonomous Sandbox Execution**: Isolated build & test execution capturing real runtime verification logs.
- 🎙️ **Live AI Technical Interview**: Multi-modal voice Q&A challenging candidate understanding of edge cases and lock contention.
- 🏅 **Dynamic 3D Skill Badges**: Interactive WebGPU medals with audio stems generated via **Lyria 3.5**.
- 🤝 **Proof-of-Skill Collaborator Matching**: Vector-similarity powered team matching based on verified GitHub credentials.

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ / Python 3.11+
- Google Gemini API Key (with `gemini-4-argon` access)
- MongoDB Atlas Connection String

### Setup & Launch

```bash
# 1. Clone the repository
git clone [https://github.com/your-username/mosa.git](https://github.com/your-username/mosa.git)
cd mosa

# 2. Configure Environment Variables
cp .env.example .env

# Fill in your API keys in .env
# GEMINI_API_KEY="your-gemini-api-key"
# MONGODB_ATLAS_URI="mongodb+srv://..."

# 3. Start Frontend & Backend
npm install && npm run dev
