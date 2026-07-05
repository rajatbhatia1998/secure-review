from typing import Dict, Any

# Global memory cache: report_id -> {"report_id": str, "step": str, "status": str, "error": str | None, "report": dict | None, "details": str}
scan_jobs: Dict[str, Dict[str, Any]] = {}

def init_job(report_id: str):
    scan_jobs[report_id] = {
        "report_id": report_id,
        "step": "scanner",
        "status": "running",
        "error": None,
        "report": None,
        "details": "Initializing..."
    }

def update_job_step(report_id: str, step: str, details: str = ""):
    if report_id in scan_jobs:
        scan_jobs[report_id]["step"] = step
        scan_jobs[report_id]["details"] = details

def complete_job(report_id: str, report_data: dict):
    if report_id in scan_jobs:
        scan_jobs[report_id]["status"] = "completed"
        scan_jobs[report_id]["step"] = "done"
        scan_jobs[report_id]["report"] = report_data
        scan_jobs[report_id]["details"] = "Scan finished!"

def fail_job(report_id: str, error_msg: str):
    if report_id in scan_jobs:
        scan_jobs[report_id]["status"] = "failed"
        scan_jobs[report_id]["error"] = error_msg
        scan_jobs[report_id]["details"] = f"Failed: {error_msg}"
