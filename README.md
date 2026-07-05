# AI Secure Review 🛡️

AI Secure Review is a powerful, open-source, multi-agent codebase auditor and security scanner. Using a **LangGraph-driven orchestration engine**, it distributes analysis workloads across specialized AI agents to scan local files for vulnerabilities, logical flaws, manifest dependencies, architectural patterns, and documentation gaps.

It includes an offline SAST engine (via Bandit) and launches a glowing, interactive React dashboard served directly from a built-in FastAPI backend.

---

## 🚀 Key Features

* **Multi-Agent Orchestration**: Distributes codebase audits to specialized, parallel agents:
  * 🔒 **Security Agent**: Scans for OWASP Top 10 vulnerabilities, hardcoded secrets, and injection flaws.
  * 🐛 **Bug Agent**: Reviews code for logical errors, memory leaks, unclosed resource handles, and race conditions.
  * 📦 **Dependency Agent**: Audits project manifest files (like `requirements.txt`, `package.json`) for outdated or insecure libraries.
  * 🏛️ **Architecture Agent**: Evaluates structural coupling, cohesion, SOLID violations, and design patterns.
  * 📝 **Documentation Agent**: Inspects docstrings, comments, and verifies repo `README.md` health.
* **Hybrid Analysis**: Combines lightning-fast offline SAST heuristics with deep LLM-based logical inspections.
* **Built-in React Dashboard**: Launches a modern, dark-themed UI served locally out of the Python package.
* **Descriptive Telemetry**: Displays which agent is currently running and exactly which files it is auditing.
* **Multi-Provider Support**: Compatible with Groq (GroqCloud), OpenAI, Google Gemini, Anthropic (Claude), Ollama (Local), and LM Studio.

---

## 📦 Installation

Install AI Secure Review via pip from your compiled wheel package:

```bash
pip install secure-review
```

### For Developers (Build from Source)
Clone the repository and compile the package automatically using our build script:
```bash
# Clone the repository
git clone https://github.com/rajatbhatia1998/secure-review.git
cd secure-review

# Run one-click compilation (requires Python build dependencies & npm)
.\build.bat

# Install the generated package
pip install dist\secure_review-1.0.0-py3-none-any.whl
```

---

## 🛠️ Commands Guide

AI Secure Review installs the global console command `secure-review`.

### 1. Doctor (System Diagnostics)
Verify your local environment dependencies (Git, Bandit) and confirm that your configured LLM provider has an active internet connection, correct credentials, and sufficient api limits:
```bash
secure-review doctor
```

### 2. Interactive Shell
Boot the core application:
```bash
secure-review
```
Executing this command automatically:
1. Starts the FastAPI backend daemon on port `8000`.
2. Launches your default web browser pointing to [http://localhost:8000/](http://localhost:8000/).
3. Enters an **interactive command console** in your terminal.

---

## 💻 Interactive Shell Commands

While inside the CLI shell, you can type `/help` to see all active console hooks:

| Command | Description |
| :--- | :--- |
| `/review` | Scan current codebase folder `.`) |
| `/review -p PATH` | Scan a specific codebase folder  |
| `/dashboard` | Re-open the React web dashboard in your default browser |
| `/config` | Interactively configure active LLM providers and API keys |
| `/providers` | Query the current active LLM configurations and check connections |
| `/doctor` | Run system tools availability checks and connection tests |
| `/clear` | Clear the console screen |
| `/help` | Print out shell documentation |
| `/exit` or `/quit` | Terminate the interactive session and backend daemon |

---

## 💻 Web Dashboard Actions
When a scan is running, the React dashboard showcases:
* **Workflow Progression**: Live node graphs syncing with backend LangGraph runs.
* **Agent Telemetry**: Dynamic details explaining which agent is currently reading which file.
* **One-Click Rescan**: Retries scans with one click after you update local files or manifest dependencies.
* **Remediation Recommendation**: Technical explanations and code-fix suggestions displayed inside IDE syntax-themed blocks.

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for details.
