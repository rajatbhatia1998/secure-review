import json
import uuid
from typing import List, Dict, Any
from backend.app.agents.base import get_llm
from backend.app.utils.repo_scanner import get_file_content
from backend.app.models.models import Issue

def run_dependency_agent(repo_path: str, files_to_review: List[str]) -> List[Issue]:
    if not files_to_review:
        return []
        
    llm = get_llm()
    issues: List[Issue] = []
    
    for file_rel in files_to_review:
        file_content = get_file_content(repo_path, file_rel)
        if not file_content:
            continue
            
        prompt = f"""You are an expert Dependency Security Engineer.
Analyze the following dependency manifest '{file_rel}' for security vulnerabilities (outdated packages, packages with known vulnerabilities/CVEs, malicious/typosquatted packages, deprecated packages).

File Content:
```
{file_content}
```

Return your findings in JSON format inside a markdown JSON code block. If no vulnerable dependencies are found, return an empty array [].
Each finding must fit the following JSON schema:
[
  {{
    "line": 12, // approximate line of the package in the file, or 1 if not clear
    "severity": "HIGH", // CRITICAL, HIGH, MEDIUM, LOW
    "title": "Vulnerable library: [package-name]",
    "description": "Short explanation of the CVE/vulnerability or deprecation in this package",
    "explanation": "Detailed explanation of why this library version is insecure, the CVE number if known, and the impact.",
    "suggested_fix": "Command to upgrade the package or target version (e.g. 'Upgrade package-name to v1.2.3')",
    "confidence": "HIGH" // HIGH, MEDIUM, LOW
  }}
]

Make sure to return valid JSON inside a ```json ``` block. Focus on known public CVEs for packages (e.g. log4j, lodash, flask, django, axios, request).
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
                    title = f.get("title", "Vulnerable Dependency")
                    
                    issue_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"dependency-{file_rel}-{line}-{title}"))
                    issues.append(Issue(
                        id=issue_id,
                        file=file_rel,
                        line=line,
                        severity=f.get("severity", "MEDIUM").upper(),
                        category="Dependency",
                        title=title,
                        description=f.get("description", ""),
                        explanation=f.get("explanation", ""),
                        suggested_fix=f.get("suggested_fix", ""),
                        confidence=f.get("confidence", "MEDIUM")
                    ))
        except Exception as e:
            print(f"[Dependency Agent] Error analyzing {file_rel}: {e}")
            
    return issues
