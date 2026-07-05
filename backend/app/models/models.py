from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class LLMConfig(BaseModel):
    provider: str = Field(default="ollama", description="LLM provider: ollama, lmstudio, openai, gemini, etc.")
    base_url: str = Field(default="http://localhost:11434", description="Base URL of the provider endpoint")
    model: str = Field(default="llama3.1", description="Model name to run queries on")
    api_key: str = Field(default="", description="API key (if required)")
    temperature: float = Field(default=0.2, description="Generation temperature")

class Issue(BaseModel):
    id: str = Field(..., description="Unique hash representing the issue")
    file: str = Field(..., description="Path to the file relative to repo root")
    line: int = Field(default=1, description="Line number of the issue")
    severity: str = Field(..., description="Severity level: CRITICAL, HIGH, MEDIUM, LOW")
    category: str = Field(..., description="Issue type: Security, Dependency, Bug, Architecture, Performance, Documentation")
    title: str = Field(..., description="Brief title of the issue")
    description: str = Field(..., description="Detailed description of the issue")
    explanation: str = Field(..., description="Deep explanation of why this is an issue and its potential impact")
    suggested_fix: str = Field(..., description="Remediation steps or code patch")
    confidence: str = Field(default="MEDIUM", description="Confidence level: HIGH, MEDIUM, LOW")

class ReviewReport(BaseModel):
    id: str = Field(..., description="Unique ID of the review report")
    target_repo: str = Field(..., description="Local path or URL of the analyzed repository")
    created_at: str = Field(..., description="ISO 8601 timestamp")
    overall_score: int = Field(default=100, description="Overall score out of 100")
    category_scores: Dict[str, int] = Field(default_factory=dict, description="Category-wise scores out of 100")
    executive_summary: str = Field(..., description="Synthesized executive summary of findings")
    issues: List[Issue] = Field(default_factory=list, description="List of detected issues")
    file_list: List[str] = Field(default_factory=list, description="Flat list of files in the repo")

class ReviewRequest(BaseModel):
    repo_path: str = Field(..., description="Absolute path or Git URL of the repository to scan")

class FixRequest(BaseModel):
    repo_path: str = Field(..., description="Absolute path of the repository")
    file: str = Field(..., description="Relative path of the target file")
    issue_id: str = Field(..., description="Vulnerability Issue ID to fix")

class FixResponse(BaseModel):
    success: bool
    original_code: str
    fixed_code: str
    patch: str
    explanation: str
