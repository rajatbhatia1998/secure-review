from typing import List, Dict, Any
from backend.app.agents.base import get_llm
from backend.app.models.models import Issue

def calculate_scores(issues: List[Issue]) -> tuple[int, Dict[str, int]]:
    # Deductions logic
    # Start with 100 for overall and for each category
    overall_deductions = 0
    categories = ["Security", "Dependency", "Bug", "Architecture", "Documentation"]
    category_issues: Dict[str, List[Issue]] = {cat: [] for cat in categories}
    
    for issue in issues:
        cat = issue.category
        if cat in category_issues:
            category_issues[cat].append(issue)
        else:
            category_issues.setdefault(cat, []).append(issue)

    def get_deductions(issue_list: List[Issue]) -> int:
        ded_sum = 0
        crit_count = 0
        high_count = 0
        med_count = 0
        low_count = 0
        
        for iss in issue_list:
            sev = iss.severity.upper()
            if sev == "CRITICAL":
                crit_count += 1
            elif sev == "HIGH":
                high_count += 1
            elif sev == "MEDIUM":
                med_count += 1
            elif sev == "LOW":
                low_count += 1
                
        # Cap deductions per severity to avoid complete wipeout from one category of low issues
        ded_sum += min(crit_count * 15, 45)
        ded_sum += min(high_count * 10, 35)
        ded_sum += min(med_count * 5, 25)
        ded_sum += min(low_count * 2, 15)
        return ded_sum

    category_scores: Dict[str, int] = {}
    for cat in categories:
        cat_iss = category_issues.get(cat, [])
        score = max(100 - get_deductions(cat_iss), 0)
        category_scores[cat.lower()] = score
        
    overall_score = int(sum(category_scores.values()) / len(categories))
    return overall_score, category_scores

def run_summary_agent(issues: List[Issue], target_repo: str) -> str:
    if not issues:
        return "No security or quality issues were detected. Codebase is in excellent health."
        
    llm = get_llm()
    
    # Summarize issues to avoid token limits
    summary_lines = []
    for iss in issues[:30]:  # Limit to first 30 issues to prevent giant prompt
        summary_lines.append(f"- [{iss.category}] [{iss.severity}] File: {iss.file}:{iss.line} - {iss.title}")
        
    issues_summary = "\n".join(summary_lines)
    if len(issues) > 30:
        issues_summary += f"\n- ... and {len(issues) - 30} more issues."

    prompt = f"""You are a Principal Security Auditor.
Synthesize an Executive Summary based on the following list of issues found in the repository '{target_repo}':

Issues:
{issues_summary}

Please generate:
1. A concise, professional Executive Summary (2-3 paragraphs) outlining the general state of the codebase, key areas of concern, and potential risks.
2. A prioritized list of 'Top Priorities' (3 items) that the engineering team should address immediately.

Return your response in markdown format. Do not repeat the individual issues list.
Executive Summary:
"""
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Audit completed with {len(issues)} issues found. Failed to generate AI summary: {e}"
