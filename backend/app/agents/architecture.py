import json
import uuid
from typing import List, Dict, Any
from backend.app.agents.base import get_llm
from backend.app.utils.repo_scanner import get_file_content
from backend.app.models.models import Issue

def run_architecture_agent(repo_path: str, files_to_review: List[str]) -> List[Issue]:
    if not files_to_review:
        return []
        
    llm = get_llm()
    issues: List[Issue] = []
    
    for file_rel in files_to_review:
        file_content = get_file_content(repo_path, file_rel)
        if not file_content:
            continue
            
        prompt = f"""You are an expert Software Architect.
Analyze the following source code file '{file_rel}' for architectural anti-patterns, design pattern violations, violation of separation of concerns, high coupling, low cohesion, or overly large and complex modules.

File Content:
```
{file_content}
```

Return your findings in JSON format inside a markdown JSON code block. If no architectural issues are found, return an empty array [].
Each finding must fit the following JSON schema:
[
  {{
    "line": 1, // usually 1 for architectural suggestions, or specific line
    "severity": "MEDIUM", // CRITICAL, HIGH, MEDIUM, LOW
    "title": "Architectural Issue: [Title]",
    "description": "Short explanation of the architectural or structural flaw",
    "explanation": "Detailed explanation of why this architectural choice scales poorly, affects maintainability, or violates standards.",
    "suggested_fix": "Refactoring plan or structural suggestion.",
    "confidence": "HIGH" // HIGH, MEDIUM, LOW
  }}
]

Make sure to return valid JSON inside a ```json ``` block. Focus on structural cleanups and class/module design.
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
                    title = f.get("title", "Architecture Finding")
                    
                    issue_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"architecture-{file_rel}-{line}-{title}"))
                    issues.append(Issue(
                        id=issue_id,
                        file=file_rel,
                        line=line,
                        severity=f.get("severity", "MEDIUM").upper(),
                        category="Architecture",
                        title=title,
                        description=f.get("description", ""),
                        explanation=f.get("explanation", ""),
                        suggested_fix=f.get("suggested_fix", ""),
                        confidence=f.get("confidence", "MEDIUM")
                    ))
        except Exception as e:
            print(f"[Architecture Agent] Error analyzing {file_rel}: {e}")
            
    return issues
