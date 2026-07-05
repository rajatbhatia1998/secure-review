import json
import uuid
from typing import List, Dict, Any
from backend.app.agents.base import get_llm
from backend.app.utils.repo_scanner import get_file_content
from backend.app.models.models import Issue
from backend.app.tools.sast_tools import run_sast_audit

def run_security_agent(repo_path: str, files_to_review: List[str], sast_issues: List[Issue]) -> List[Issue]:
    if not files_to_review:
        return []
        
    llm = get_llm()
    issues: List[Issue] = []
    
    # Associate SAST findings by file
    sast_by_file: Dict[str, List[Issue]] = {}
    for issue in sast_issues:
        sast_by_file.setdefault(issue.file, []).append(issue)
        
    for file_rel in files_to_review:
        file_content = get_file_content(repo_path, file_rel)
        if not file_content:
            continue
            
        file_sast = sast_by_file.get(file_rel, [])
        sast_context = ""
        if file_sast:
            sast_context = "The static analysis tool found the following warnings in this file:\n"
            for s in file_sast:
                sast_context += f"- Line {s.line}: [{s.severity}] {s.title} - {s.description}\n"
                
        prompt = f"""You are an expert AI Security Engineer.
Analyze the following code file '{file_rel}' for security vulnerabilities (SQL Injection, XSS, CSRF, broken authentication, hardcoded secrets, insecure deserialization, path traversal, OWASP Top 10).

{sast_context}

File Content:
```
{file_content}
```

Return your findings in JSON format inside a markdown JSON code block. If no vulnerabilities are found, return an empty array [].
Each vulnerability must fit the following JSON schema:
[
  {{
    "line": 15,
    "severity": "HIGH", // CRITICAL, HIGH, MEDIUM, LOW
    "title": "Short title of vulnerability",
    "description": "Short summary of the bug",
    "explanation": "Detailed explanation of the risk, why it matters, and how it can be exploited.",
    "suggested_fix": "Remediation code snippet or specific refactoring steps.",
    "confidence": "HIGH" // HIGH, MEDIUM, LOW
  }}
]

Make sure to return valid JSON inside a ```json ``` block. Avoid duplicate findings. Double check line numbers based on the file content.
JSON Output:
"""
        try:
            response = llm.invoke(prompt)
            content = response.content
            
            # Extract JSON block
            json_str = ""
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
                
            findings = json.loads(json_str)
            if isinstance(findings, list):
                for f in findings:
                    line = f.get("line", 1)
                    title = f.get("title", "Security Vulnerability")
                    
                    issue_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"security-{file_rel}-{line}-{title}"))
                    issues.append(Issue(
                        id=issue_id,
                        file=file_rel,
                        line=line,
                        severity=f.get("severity", "MEDIUM").upper(),
                        category="Security",
                        title=title,
                        description=f.get("description", ""),
                        explanation=f.get("explanation", ""),
                        suggested_fix=f.get("suggested_fix", ""),
                        confidence=f.get("confidence", "MEDIUM")
                    ))
        except Exception as e:
            # Fall back to returning SAST issues if LLM fails or returns invalid format
            for s in file_sast:
                if s not in issues:
                    issues.append(s)
            
    # Include all remaining SAST issues that weren't refined
    for s in sast_issues:
        if s.file not in files_to_review:
            all_files_in_issues = [iss.id for iss in issues]
            if s.id not in all_files_in_issues:
                issues.append(s)
                
    return issues
