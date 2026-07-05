from typing import Dict, Any, List
from pathlib import Path

# Deterministic routing based on file types
def run_planner(scan_result: Dict[str, Any]) -> Dict[str, List[str]]:
    files = scan_result.get("files", [])
    
    # Filter files into categories
    security_candidates = []
    bug_candidates = []
    arch_candidates = []
    dep_candidates = []
    doc_candidates = []

    # Important file markers to prioritize
    priority_keywords = {"main", "app", "server", "index", "route", "controller", "db", "auth", "config", "util"}

    for f in files:
        f_lower = f.lower()
        path = Path(f)
        ext = path.suffix.lower()

        # Dependencies
        if path.name.lower() in ("package.json", "requirements.txt", "go.mod", "cargo.toml", "pipfile", "pyproject.toml"):
            dep_candidates.append(f)
            
        # Documentation
        elif ext in (".md", ".txt", ".rst") or "docs/" in f_lower or "doc/" in f_lower:
            doc_candidates.append(f)
            
        # Code files
        elif ext in (".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".cs", ".php", ".rb", ".sh"):
            # Check if it has priority keywords or is relatively small/medium
            is_priority = any(k in path.stem.lower() for k in priority_keywords)
            
            # Security targets authentication, db, routes, or priority files
            if is_priority or any(x in f_lower for x in ("auth", "db", "sql", "api", "route", "controller")):
                security_candidates.append(f)
            else:
                # Add up to 5 general code files to keep it fast
                if len(security_candidates) < 10:
                    security_candidates.append(f)

            # Bug / quality targets general code files
            if is_priority or len(bug_candidates) < 10:
                bug_candidates.append(f)

            # Architecture looks at main structures, imports, and config files
            if is_priority or len(arch_candidates) < 8:
                arch_candidates.append(f)

    # Fallbacks if list is empty but files exist
    if not security_candidates and files:
        security_candidates = [f for f in files if Path(f).suffix.lower() in (".py", ".js", ".ts", ".tsx")][:5]
    if not bug_candidates and files:
        bug_candidates = [f for f in files if Path(f).suffix.lower() in (".py", ".js", ".ts", ".tsx")][:5]
    if not arch_candidates and files:
        arch_candidates = [f for f in files if Path(f).suffix.lower() in (".py", ".js", ".ts", ".tsx")][:5]

    return {
        "security": security_candidates,
        "dependency": dep_candidates,
        "bug": bug_candidates,
        "architecture": arch_candidates,
        "documentation": doc_candidates
    }
