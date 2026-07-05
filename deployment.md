# Deployment Guide: Python Package with Built-in React UI

This guide documents how to compile the Vite React frontend and bundle it into a single, redistributable Python package (`.whl` / `.tar.gz`). When a user installs the package, they can start the backend FastAPI server and access the interactive web dashboard natively.

---

## Prerequisites

Ensure you have Python 3.10+ and Node.js (with npm) installed.

Ensure the build dependencies are installed in your virtual environment:
```bash
pip install --upgrade setuptools wheel build
```

---

## Directory Structure Alignment

To serve the React UI out of the Python package, the compiled files are structured inside the package under `backend/app/dist/`:

```text
security-cli/
├── backend/
│   └── app/
│       ├── dist/               <-- Copy compiled Vite build here
│       │   ├── assets/
│       │   └── index.html
│       ├── main.py             <-- Configured to serve files from Path(__file__).parent / "dist"
│       └── cli.py
├── frontend/
│   ├── dist/                   <-- Vite compiles assets here
│   └── src/
├── setup.py                    <-- Configured to bundle backend/app/dist as package data
└── build_package.py            <-- Python automation build script
```

---

## Automatic Build Procedure

We have provided an automated build script: [build_package.py](file:///g:/Software%20Development/security-cli/build_package.py).

Run the script from your workspace root:
```bash
.\venv\Scripts\python.exe build_package.py
```

This script will automatically:
1. Compile the Vite React frontend to production static files.
2. Clean and replace the target `backend/app/dist` directory.
3. Bundle the static files and compile the wheel package using Python's standard `build` module.

---

## Manual Build Procedure

If you prefer to perform the steps manually:

1. **Build Vite React Assets**:
   Change to the `frontend` directory and run:
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

2. **Clean & Copy Build Folder**:
   Copy the `dist` directory from the frontend into the backend application folder.
   On Windows PowerShell:
   ```powershell
   Remove-Item -Recurse -Force backend/app/dist
   Copy-Item -Recurse frontend/dist backend/app/dist
   ```
   On Linux/macOS:
   ```bash
   rm -rf backend/app/dist
   cp -r frontend/dist backend/app/dist
   ```

3. **Build the Python Distribution Packages**:
   Compile the source distribution and wheel binary:
   ```bash
   python -m build
   ```
   This will output the compiled `.whl` and `.tar.gz` packages inside a root `dist/` directory.

---

## Installing and Running the Package

### 1. Installation
Install the compiled wheel package onto any system:
```bash
pip install dist/secure_review-1.0.0-py3-none-any.whl
```

### 2. Execution
Run the CLI or start the dashboard directly:
```bash
# Start interactive console and automatically boot the web server & dashboard browser:
secure-review

# Run doctor connection checks:
secure-review doctor
```
Once started, the backend server will serve the built-in React UI directly at:
[http://localhost:8000/](http://localhost:8000/)
