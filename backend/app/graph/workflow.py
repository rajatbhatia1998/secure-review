import uuid
from typing import TypedDict, List, Dict, Any, Annotated, Optional
from langgraph.graph import StateGraph, END
from backend.app.models.models import Issue, ReviewReport
from backend.app.utils.repo_scanner import scan_directory
from backend.app.tools.sast_tools import run_sast_audit
from backend.app.agents.planner import run_planner
from backend.app.agents.security import run_security_agent
from backend.app.agents.dependency import run_dependency_agent
from backend.app.agents.bug import run_bug_agent
from backend.app.agents.architecture import run_architecture_agent
from backend.app.agents.documentation import run_documentation_agent
from backend.app.agents.summary import calculate_scores, run_summary_agent
from backend.app.utils.progress import update_job_step

# Define Agent State
class AgentState(TypedDict):
    repo_path: str
    files: List[str]
    languages: Dict[str, int]
    dominant_language: str
    package_managers: List[str]
    frameworks: List[str]
    allocated_files: Dict[str, List[str]]
    sast_issues: List[Issue]
    issues: List[Issue]
    overall_score: int
    category_scores: Dict[str, int]
    executive_summary: str
    report_id: str

# 1. Scanner Node
def scanner_node(state: AgentState) -> Dict[str, Any]:
    update_job_step(state.get("report_id"), "scanner", "Scanning repository directories & mapping structure...")
    scan_res = scan_directory(state["repo_path"])
    return {
        "files": scan_res["files"],
        "languages": scan_res["languages"],
        "dominant_language": scan_res["dominant_language"],
        "package_managers": scan_res["package_managers"],
        "frameworks": scan_res["frameworks"],
    }

# 2. SAST Node
def sast_node(state: AgentState) -> Dict[str, Any]:
    update_job_step(state.get("report_id"), "sast", "Auditing with offline Python Bandit and regex SAST checks...")
    sast_issues = run_sast_audit(state["repo_path"], state["files"])
    return {"sast_issues": sast_issues}

# 3. Planner Node
def planner_node(state: AgentState) -> Dict[str, Any]:
    update_job_step(state.get("report_id"), "planner", "Routing codebase analysis tasks to specialized agents...")
    scan_res = {
        "files": state["files"],
        "languages": state["languages"],
        "package_managers": state["package_managers"],
        "frameworks": state["frameworks"],
    }
    allocated = run_planner(scan_res)
    return {"allocated_files": allocated}

# 4. Security Agent Node
def security_node(state: AgentState) -> Dict[str, Any]:
    sec_files = state["allocated_files"].get("security", [])
    files_info = f": {', '.join(sec_files[:3])}" if sec_files else ""
    if len(sec_files) > 3:
        files_info += f" (+{len(sec_files)-3} more)"
    update_job_step(state.get("report_id"), "agents", f"Security Agent: Reviewing OWASP security vulnerabilities{files_info}...")
    issues = run_security_agent(state["repo_path"], sec_files, state["sast_issues"])
    return {"issues": state.get("issues", []) + issues}

# 5. Dependency Agent Node
def dependency_node(state: AgentState) -> Dict[str, Any]:
    dep_files = state["allocated_files"].get("dependency", [])
    files_info = f": {', '.join(dep_files[:3])}" if dep_files else ""
    if len(dep_files) > 3:
        files_info += f" (+{len(dep_files)-3} more)"
    update_job_step(state.get("report_id"), "agents", f"Dependency Agent: Auditing manifest credentials & CVEs{files_info}...")
    issues = run_dependency_agent(state["repo_path"], dep_files)
    return {"issues": state.get("issues", []) + issues}

# 6. Bug Agent Node
def bug_node(state: AgentState) -> Dict[str, Any]:
    bug_files = state["allocated_files"].get("bug", [])
    files_info = f": {', '.join(bug_files[:3])}" if bug_files else ""
    if len(bug_files) > 3:
        files_info += f" (+{len(bug_files)-3} more)"
    update_job_step(state.get("report_id"), "agents", f"Bug Agent: Scanning for logic flaws & runtime exceptions{files_info}...")
    issues = run_bug_agent(state["repo_path"], bug_files)
    return {"issues": state.get("issues", []) + issues}

# 7. Architecture Agent Node
def architecture_node(state: AgentState) -> Dict[str, Any]:
    arch_files = state["allocated_files"].get("architecture", [])
    files_info = f": {', '.join(arch_files[:3])}" if arch_files else ""
    if len(arch_files) > 3:
        files_info += f" (+{len(arch_files)-3} more)"
    update_job_step(state.get("report_id"), "agents", f"Architecture Agent: Auditing structural designs & cohesion{files_info}...")
    issues = run_architecture_agent(state["repo_path"], arch_files)
    return {"issues": state.get("issues", []) + issues}

# 8. Documentation Agent Node
def documentation_node(state: AgentState) -> Dict[str, Any]:
    doc_files = state["allocated_files"].get("documentation", [])
    files_info = f": {', '.join(doc_files[:3])}" if doc_files else ""
    if len(doc_files) > 3:
        files_info += f" (+{len(doc_files)-3} more)"
    update_job_step(state.get("report_id"), "agents", f"Documentation Agent: Scanning docstrings & README files{files_info}...")
    issues = run_documentation_agent(state["repo_path"], doc_files)
    return {"issues": state.get("issues", []) + issues}

# 9. Summary/Compiler Node
def summary_node(state: AgentState) -> Dict[str, Any]:
    update_job_step(state.get("report_id"), "summary", "Compiling scores and writing executive reports...")
    all_issues = []
    seen_ids = set()
    
    raw_issues_list = state.get("issues", [])
    if not isinstance(raw_issues_list, list):
         raw_issues_list = []
         
    for iss in raw_issues_list:
        if iss.id not in seen_ids:
            all_issues.append(iss)
            seen_ids.add(iss.id)
            
    overall, cat_scores = calculate_scores(all_issues)
    exec_summary = run_summary_agent(all_issues, state["repo_path"])
    
    return {
        "issues": all_issues,
        "overall_score": overall,
        "category_scores": cat_scores,
        "executive_summary": exec_summary
    }

# Create Graph
def create_review_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("scanner", scanner_node)
    workflow.add_node("sast", sast_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("security_agent", security_node)
    workflow.add_node("dependency_agent", dependency_node)
    workflow.add_node("bug_agent", bug_node)
    workflow.add_node("architecture_agent", architecture_node)
    workflow.add_node("documentation_agent", documentation_node)
    workflow.add_node("summary", summary_node)
    
    # Define Edges
    workflow.set_entry_point("scanner")
    workflow.add_edge("scanner", "sast")
    workflow.add_edge("sast", "planner")
    
    workflow.add_edge("planner", "security_agent")
    workflow.add_edge("security_agent", "dependency_agent")
    workflow.add_edge("dependency_agent", "bug_agent")
    workflow.add_edge("bug_agent", "architecture_agent")
    workflow.add_edge("architecture_agent", "documentation_agent")
    workflow.add_edge("documentation_agent", "summary")
    workflow.add_edge("summary", END)
    
    return workflow.compile()

# Helper to run the review workflow
def run_review_workflow(repo_path: str, report_id: Optional[str] = None) -> Dict[str, Any]:
    app = create_review_graph()
    if not report_id:
        report_id = str(uuid.uuid4())
    
    initial_state = {
        "repo_path": repo_path,
        "files": [],
        "languages": {},
        "dominant_language": "",
        "package_managers": [],
        "frameworks": [],
        "allocated_files": {},
        "sast_issues": [],
        "issues": [],
        "overall_score": 100,
        "category_scores": {},
        "executive_summary": "",
        "report_id": report_id
    }
    
    result = app.invoke(initial_state)
    return result
