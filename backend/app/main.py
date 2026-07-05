import os
import json
import difflib
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.app.config.config import load_config, save_config
from backend.app.models.models import (
    LLMConfig, ReviewReport, ReviewRequest, Issue,
    FixRequest, FixResponse
)
from backend.app.graph.workflow import run_review_workflow
from backend.app.agents.base import get_llm

app = FastAPI(title="AI Secure Review API", version="1.0")

# Enable CORS for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORTS_DIR = Path(os.path.expanduser("~")) / ".secure-review" / "reports"

def find_issue_in_reports(issue_id: str) -> Optional[tuple[dict, dict]]:
    if not REPORTS_DIR.exists():
        return None
    for report_file in REPORTS_DIR.glob("*.json"):
        try:
            with open(report_file, "r") as f:
                report = json.load(f)
                for issue in report.get("issues", []):
                    if issue.get("id") == issue_id:
                        return issue, report
        except Exception:
            continue
    return None

@app.get("/health")
def health():
    return {"status": "ok", "service": "AI Secure Review API"}

def clean_error_message(e: Exception) -> str:
    err_msg = str(e)
    if hasattr(e, "message") and e.message:
        return e.message
    import re
    match = re.search(r"['\"]message['\"]\s*:\s*['\"]([^'\"]+)['\"]", err_msg)
    if match:
        return match.group(1).replace("\\n", "\n")
    return err_msg

@app.get("/providers")
def get_providers():
    config = load_config()
    llm_ok = True
    llm_error = ""
    try:
        llm = get_llm()
        llm.invoke("ping", config={"timeout": 3.0})
    except Exception as e:
        llm_ok = False
        llm_error = clean_error_message(e)
        
    return {
        "current": config.provider,
        "model": config.model,
        "base_url": config.base_url,
        "api_key": "******" if config.api_key else "",
        "available": ["ollama", "lmstudio", "openai", "gemini", "groq", "openai-compatible"],
        "llm_ok": llm_ok,
        "llm_error": llm_error
    }

@app.post("/config")
def update_config(new_config: LLMConfig):
    old_config = load_config()
    # Preserve the existing API key if it's sent as empty/obfuscated and provider did not change
    if new_config.provider == old_config.provider:
        if not new_config.api_key or new_config.api_key == "******":
            new_config.api_key = old_config.api_key
    save_config(new_config)
    return {"status": "success", "message": "Configuration updated successfully"}

from backend.app.utils.progress import init_job, complete_job, fail_job, scan_jobs
import uuid

def make_serializable(obj: Any) -> Any:
    if isinstance(obj, list):
        return [make_serializable(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif hasattr(obj, "model_dump"):
        return make_serializable(obj.model_dump())
    elif hasattr(obj, "dict"):
        return make_serializable(obj.dict())
    return obj

def run_background_review(repo_path: str, report_id: str):
    init_job(report_id)
    try:
        result = run_review_workflow(repo_path, report_id)
        serializable_result = make_serializable(result)
        # Save report to disk
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_file = REPORTS_DIR / f"{report_id}.json"
        with open(report_file, "w") as f:
            json.dump(serializable_result, f, indent=2)
        complete_job(report_id, serializable_result)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(tb)
        fail_job(report_id, str(e))

@app.post("/review")
def start_review(request: ReviewRequest, background_tasks: BackgroundTasks):
    path = request.repo_path
    if path.startswith(("http://", "https://", "git@")):
        raise HTTPException(status_code=400, detail="Only local repositories are allowed for scanning.")
    if not os.path.exists(path) or not os.path.isdir(path):
        raise HTTPException(status_code=400, detail=f"Local path '{path}' does not exist or is not a directory.")
            
    report_id = str(uuid.uuid4())
    background_tasks.add_task(run_background_review, path, report_id)
    return {"report_id": report_id, "step": "scanner", "status": "running"}

@app.get("/review/{report_id}/status")
def get_review_status(report_id: str):
    if report_id in scan_jobs:
        return scan_jobs[report_id]
        
    report_file = REPORTS_DIR / f"{report_id}.json"
    if report_file.exists():
        try:
            with open(report_file, "r") as f:
                report_data = json.load(f)
            return {
                "report_id": report_id,
                "step": "done",
                "status": "completed",
                "report": report_data
            }
        except Exception:
            pass
            
    raise HTTPException(status_code=404, detail="Audit job not found.")

@app.get("/report/{report_id}")
def get_report(report_id: str):
    report_file = REPORTS_DIR / f"{report_id}.json"
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    try:
        with open(report_file, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load report: {str(e)}")

@app.post("/fix", response_model=FixResponse)
def apply_fix(request: FixRequest):
    # Locate issue
    issue_data = find_issue_in_reports(request.issue_id)
    if not issue_data:
        raise HTTPException(status_code=404, detail=f"Issue with ID '{request.issue_id}' not found in saved reports.")
        
    issue, report = issue_data
    file_rel = issue.get("file")
    
    # Read original file content
    full_path = Path(request.repo_path) / file_rel
    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"Target file '{file_rel}' not found at repository path.")
        
    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            original_code = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read target file: {str(e)}")
        
    # Query LLM to generate fix
    llm = get_llm()
    prompt = f"""You are a Senior Software Engineer. Fix the following code security or quality issue.

File Path: {file_rel}
Line: {issue.get('line')}
Issue Category: {issue.get('category')}
Issue Title: {issue.get('title')}
Issue Description: {issue.get('description')}
Remediation Recommendation: {issue.get('suggested_fix')}

Original File Content:
```
{original_code}
```

Please output the COMPLETE fixed file content. Do not include any markdown comments, intro, or formatting outside the code block.
Return the complete code inside a standard markdown code block starting with ``` and ending with ```.
Fixed Code:
"""
    try:
        response = llm.invoke(prompt)
        content = response.content
        
        # Parse output code from markdown block
        fixed_code = content
        if "```" in content:
            parts = content.split("```")
            # Usually the second part contains the code
            for part in parts:
                cleaned_part = part.strip()
                if cleaned_part:
                    # If it starts with language identifier, strip first line
                    lines = cleaned_part.splitlines()
                    if len(lines) > 1 and lines[0].strip() in ("python", "javascript", "typescript", "go", "rust", "html", "css", "json", "sh", "bash"):
                        fixed_code = "\n".join(lines[1:])
                    else:
                        fixed_code = cleaned_part
                    break
                    
        # Generate unified diff patch
        diff_lines = list(difflib.unified_diff(
            original_code.splitlines(keepends=True),
            fixed_code.splitlines(keepends=True),
            fromfile=f"a/{file_rel}",
            tofile=f"b/{file_rel}"
        ))
        patch = "".join(diff_lines)
        
        explanation = f"Applied automated remediation to resolve: {issue.get('title')} ({issue.get('severity')} priority)."
        
        return FixResponse(
            success=True,
            original_code=original_code,
            fixed_code=fixed_code,
            patch=patch,
            explanation=explanation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM remediation generation failed: {str(e)}")

@app.get("/file")
def get_file_endpoint(repo_path: str, file_path: str):
    full_path = Path(repo_path) / file_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class WriteFileRequest(BaseModel):
    repo_path: str
    file_path: str
    content: str

@app.post("/write-file")
def write_file_endpoint(request: WriteFileRequest):
    full_path = Path(request.repo_path) / request.file_path
    try:
        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(request.content)
        return {"status": "success", "message": "File written successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static compiled frontend files in production
FRONTEND_DIST = Path(__file__).parent / "dist"

if FRONTEND_DIST.exists():
    # Mount assets folder first so it doesn't get shadowed by root route
    if (FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")
        
    # Serve index.html for root or any unhandled client paths (SPA routing fallback)
    @app.get("/")
    @app.get("/{path_name:path}")
    def serve_frontend(path_name: str = ""):
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "API is running. Build frontend static assets to view the dashboard."}
