import os
import re
import subprocess
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any
from backend.app.models.models import Issue

# Basic regex for secrets detection
SECRET_PATTERNS = {
    "AWS API Key": r"AKIA[0-9A-Z]{16}",
    "Generic Private Key": r"-----BEGIN[ A-Z0-9_-]+PRIVATE KEY-----",
    "Generic Secret / Token / Password": r"(?i)(api_key|apikey|secret|password|passwd|auth_token|token|access_token|private_key)\s*[:=]\s*['\"][A-Za-z0-9/+=_-]{16,}['\"]",
    "Slack Webhook URL": r"https://hooks\.slack\.com/services/[T][A-Za-z0-9_]{8}/[B][A-Za-z0-9_]{8}/[A-Za-z0-9_]{24}",
    "Database Credentials URI": r"mongodb(\+srv)?://|postgres(ql)?://|mysql://|redis://",
}

# Regex for security checks (SQLi, XSS, eval, shell=True)
CODE_PATTERNS = {
    "SQL Injection Pattern": (
        r"(?i)\.(execute|rawQuery|query)\s*\(\s*(f['\"]|['\"].*?\+.*?['\"]|['\"].*?%|.*?.format\()",
        "Avoid raw query concatenation. Use parameterized queries/prepared statements instead.",
        "CRITICAL",
        "Security"
    ),
    "Unsafe Eval/Exec Use": (
        r"\b(eval|exec)\s*\(",
        "Dynamically executing user code via eval() or exec() can lead to remote code execution (RCE).",
        "HIGH",
        "Security"
    ),
    "Command Injection Potential": (
        r"\bsubprocess\.(run|Popen|call)\s*\([^)]*shell\s*=\s*True",
        "Running subprocess with shell=True is dangerous and can lead to command injection if input is untrusted.",
        "HIGH",
        "Security"
    ),
    "Insecure React innerHTML": (
        r"dangerouslySetInnerHTML\s*=\s*\{\s*\{\s*__html\s*:",
        "Using dangerouslySetInnerHTML skips standard XSS protection. Ensure input is properly sanitized.",
        "HIGH",
        "Security"
    ),
    "Insecure JS innerHTML": (
        r"\.innerHTML\s*=",
        "Setting element.innerHTML directly can lead to Cross-Site Scripting (XSS) if input contains user data.",
        "MEDIUM",
        "Security"
    )
}

def run_bandit(repo_path: str) -> List[Issue]:
    issues: List[Issue] = []
    # Find if bandit is installed in venv or globally
    bandit_executable = "bandit"
    # Check inside local virtual env
    venv_bandit = Path(repo_path) / "venv" / "Scripts" / "bandit.exe"
    if venv_bandit.exists():
        bandit_executable = str(venv_bandit)
    elif os.path.exists(r".\venv\Scripts\bandit.exe"):
        bandit_executable = r".\venv\Scripts\bandit.exe"
        
    try:
        # Run bandit in JSON output mode
        cmd = [bandit_executable, "-r", ".", "-f", "json"]
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
        if result.stdout:
            data = json.loads(result.stdout)
            results = data.get("results", [])
            for res in results:
                file_rel = res.get("filename", "")
                # Normalize path separators
                file_rel = file_rel.replace('\\', '/')
                line = res.get("line_number", 1)
                sev = res.get("issue_severity", "MEDIUM").upper()
                conf = res.get("issue_confidence", "MEDIUM").upper()
                title = res.get("issue_text", "Bandit Security Finding")
                desc = f"Bandit finding: {res.get('issue_text')}. Rule ID: {res.get('test_id')}"
                expl = f"More details: {res.get('more_info') or 'N/A'}"
                fix = "Review codebase context and apply safer alternatives or input validation."
                
                issue_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"bandit-{file_rel}-{line}-{title}"))
                
                issues.append(Issue(
                    id=issue_id,
                    file=file_rel,
                    line=line,
                    severity=sev if sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] else "MEDIUM",
                    category="Security",
                    title=title,
                    description=desc,
                    explanation=expl,
                    suggested_fix=fix,
                    confidence=conf
                ))
    except Exception as e:
        # Bandit failed or wasn't installed, return empty
        pass
    return issues

def scan_file_heuristics(repo_path: str, relative_path: str) -> List[Issue]:
    issues: List[Issue] = []
    full_path = Path(repo_path) / relative_path
    if not full_path.exists() or full_path.is_dir():
        return []

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            
        file_content = "".join(lines)
        
        # 1. Check Secrets
        for name, pattern in SECRET_PATTERNS.items():
            matches = re.finditer(pattern, file_content)
            for match in matches:
                # Find line number
                start_char = match.start()
                line_no = file_content.count("\n", 0, start_char) + 1
                matched_text = match.group(0)
                # Obfuscate secret in reports
                obfuscated = matched_text[:len(matched_text)//4] + "..." + matched_text[-4:] if len(matched_text) > 8 else "********"
                
                issue_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"secret-{relative_path}-{line_no}-{name}"))
                issues.append(Issue(
                    id=issue_id,
                    file=relative_path,
                    line=line_no,
                    severity="CRITICAL",
                    category="Security",
                    title=f"Exposed Secret Detected: {name}",
                    description=f"A pattern matching an {name} ({obfuscated}) was found hardcoded in source code.",
                    explanation="API keys, connection strings, and certificates must not be stored in raw code files. If the repository is public or accessed by unauthorized users, these credentials will be leaked.",
                    suggested_fix="Remove the credential immediately. Replace it with an environment variable or load it dynamically using a secure vaults manager (e.g. HashiCorp Vault, AWS Secrets Manager, .env file). Revoke the exposed credential immediately.",
                    confidence="HIGH"
                ))

        # 2. Check Code Anti-patterns
        for pattern_name, (pattern, rule_desc, severity, category) in CODE_PATTERNS.items():
            # Only apply react check for jsx/tsx, js check for js/ts, etc.
            if "React" in pattern_name and not relative_path.endswith((".jsx", ".tsx")):
                continue
            
            matches = re.finditer(pattern, file_content)
            for match in matches:
                start_char = match.start()
                line_no = file_content.count("\n", 0, start_char) + 1
                
                issue_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"code-{relative_path}-{line_no}-{pattern_name}"))
                issues.append(Issue(
                    id=issue_id,
                    file=relative_path,
                    line=line_no,
                    severity=severity,
                    category=category,
                    title=pattern_name,
                    description=rule_desc,
                    explanation=f"Regex match detected dynamic risk {pattern_name}. This is a common static linting violation.",
                    suggested_fix="Refactor the code to eliminate this pattern. Refer to language best practices.",
                    confidence="MEDIUM"
                ))
    except Exception:
        pass
    return issues

def run_sast_audit(repo_path: str, file_list: List[str]) -> List[Issue]:
    all_issues: List[Issue] = []
    
    # Run bandit on python projects
    python_files = [f for f in file_list if f.endswith(".py")]
    if python_files:
        all_issues.extend(run_bandit(repo_path))
        
    # Run regex scanner on all files
    for file_rel in file_list:
        # Ignore requirements.txt, yarn.lock, etc. in heuristics (they are scanned in dependency agent)
        if file_rel.endswith(("requirements.txt", "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml")):
            continue
        all_issues.extend(scan_file_heuristics(repo_path, file_rel))
        
    return all_issues
