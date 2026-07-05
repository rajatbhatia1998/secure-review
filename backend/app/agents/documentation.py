import json
import uuid
from typing import List, Dict, Any
from backend.app.agents.base import get_llm
from backend.app.utils.repo_scanner import get_file_content
from backend.app.models.models import Issue

def run_documentation_agent(repo_path: str, files_to_review: List[str]) -> List[Issue]:
    issues: List[Issue] = []
    
    # Check if a README.md exists in the root or subfolders
    import os
    readme_exists = False
    for root, dirs, files in os.walk(repo_path):
        # Prevent searching inside ignored directories
        dirs[:] = [d for d in dirs if d not in (".git", "venv", "node_modules", ".pytest_cache", "__pycache__")]
        if any(f.lower() == "readme.md" for f in files):
            readme_exists = True
            break
            
    if not readme_exists:
        issue_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"documentation-missing-readme-{repo_path}"))
        issues.append(Issue(
            id=issue_id,
            file="README.md",
            line=1,
            severity="HIGH",
            category="Documentation",
            title="Missing Repository Documentation (README.md)",
            description="The repository does not contain a README.md file in the root or directories.",
            explanation="A README.md file is critical for onboarding developers, detailing project setup guidelines, specifying dependencies, and explaining utility usages. Lacking it makes code maintenance difficult.",
            suggested_fix="Create a README.md file in the root directory outlining the project name, description, setup commands, and architecture overview.",
            confidence="HIGH"
        ))

    if not files_to_review:
        if readme_exists:
            # Find the actual path of the README.md
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs if d not in (".git", "venv", "node_modules", ".pytest_cache", "__pycache__")]
                for f in files:
                    if f.lower() == "readme.md":
                        rel_path = os.path.relpath(os.path.join(root, f), repo_path).replace('\\', '/')
                        files_to_review = [rel_path]
                        break
                if files_to_review:
                    break
        else:
            return issues
            
    llm = get_llm()
    
    for file_rel in files_to_review:
        file_content = get_file_content(repo_path, file_rel)
        if not file_content:
            continue
            
        prompt = f"""You are an expert technical writer and code auditor.
Analyze the following document or code file '{file_rel}' for documentation completeness, clarity, accuracy, missing setup guides, missing docstrings, or obsolete comments.

File Content:
```
{file_content}
```

Return your findings in JSON format inside a markdown JSON code block. If no documentation issues are found, return an empty array [].
Each finding must fit the following JSON schema:
[
  {{
    "line": 1,
    "severity": "LOW", // CRITICAL, HIGH, MEDIUM, LOW
    "title": "Documentation Issue: [Title]",
    "description": "Short explanation of the missing or incomplete documentation item",
    "explanation": "Detailed explanation of why having this documentation matters for developers, users, or contributors.",
    "suggested_fix": "Write down the recommended text or docstring to add, or outline a README structure.",
    "confidence": "HIGH" // HIGH, MEDIUM, LOW
  }}
]

Make sure to return valid JSON inside a ```json ``` block. Focus on usability and developer onboarding.
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
                    title = f.get("title", "Documentation Finding")
                    
                    issue_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"documentation-{file_rel}-{line}-{title}"))
                    issues.append(Issue(
                        id=issue_id,
                        file=file_rel,
                        line=line,
                        severity=f.get("severity", "LOW").upper(),
                        category="Documentation",
                        title=title,
                        description=f.get("description", ""),
                        explanation=f.get("explanation", ""),
                        suggested_fix=f.get("suggested_fix", ""),
                        confidence=f.get("confidence", "MEDIUM")
                    ))
        except Exception as e:
            print(f"[Documentation Agent] Error analyzing {file_rel}: {e}")
            
    return issues
