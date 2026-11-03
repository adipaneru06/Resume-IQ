"""
Resumely AI — Pydantic Schemas for Resume Analysis
Strictly defines the structure and validation rules for Gemini output and API responses.
Includes intelligent pre-validators and aliases for resilient LLM decoding.
"""

from typing import List, Optional, Literal, Union, Dict, Any
from pydantic import BaseModel, Field, AliasChoices, model_validator


class ATSCheck(BaseModel):
    label: str = Field(description="Name of the ATS check")
    passed: bool = Field(description="Whether the resume passed this check")
    note: str = Field(description="Explanation or recommendation regarding this check")


class ATSResult(BaseModel):
    score: int = Field(ge=0, le=100, description="ATS parsability score from 0 to 100")
    checks: List[ATSCheck] = Field(description="List of granular ATS compatibility checks")


class JobMatchResult(BaseModel):
    percentage: int = Field(ge=0, le=100, description="Role alignment match percentage from 0 to 100")
    matched_keywords: List[str] = Field(default_factory=list, description="Keywords present in resume matching role")
    missing_keywords: List[str] = Field(default_factory=list, description="Important role keywords missing from resume")


class CriterionScore(BaseModel):
    name: str = Field(description="Name of the rubric criterion matching config.py")
    score: int = Field(ge=0, le=100, description="Score for this criterion (0-100)")
    reasoning: str = Field(default="", description="Brief qualitative assessment for this score")


class SectionEvaluation(BaseModel):
    name: str = Field(description="Standard resume section name")
    score: int = Field(ge=0, le=100, description="Section benchmark score (0-100)")
    reasoning: str = Field(default="", description="Assessment of section quality and depth")
    suggestions: List[str] = Field(default_factory=list, description="Specific suggestions for this section")


class PrioritizedSuggestion(BaseModel):
    priority: Literal["high", "medium", "low"] = Field(description="Priority ranking")
    issue: str = Field(description="Specific resume deficiency identified")
    fix: str = Field(description="Actionable recommendation to resolve the issue")

    @model_validator(mode="before")
    @classmethod
    def normalize_priority(cls, data: Any) -> Any:
        if isinstance(data, dict):
            p = str(data.get("priority", "medium")).lower()
            if "high" in p:
                data["priority"] = "high"
            elif "low" in p:
                data["priority"] = "low"
            else:
                data["priority"] = "medium"
        return data


class BulletRewrite(BaseModel):
    before: str = Field(
        validation_alias=AliasChoices("before", "original", "old", "input"),
        description="Original vague or weak bullet point from resume"
    )
    after: str = Field(
        validation_alias=AliasChoices("after", "rewrite", "improved", "new", "revised"),
        description="Action-oriented, quantified rewrite"
    )
    why: str = Field(
        default="",
        validation_alias=AliasChoices("why", "reason", "explanation", "impact"),
        description="Explanation of why the rewrite is more impactful"
    )


class LanguageIssue(BaseModel):
    type: str = Field(
        default="grammar",
        description="Category of language issue"
    )
    original: str = Field(
        default="",
        validation_alias=AliasChoices("original", "issue", "phrase", "text", "before"),
        description="Original problematic phrasing or sentence"
    )
    suggestion: str = Field(
        default="",
        validation_alias=AliasChoices("suggestion", "fix", "replacement", "after"),
        description="Recommended correction or alternative"
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_language_issue(cls, data: Any) -> Any:
        if isinstance(data, dict):
            t = str(data.get("type", "grammar")).lower()
            if "passive" in t:
                data["type"] = "passive"
            elif "buzz" in t or "clich" in t or "platitude" in t:
                data["type"] = "buzzword"
            elif "long" in t or "wordy" in t or "sentence" in t or "length" in t:
                data["type"] = "long_sentence"
            else:
                data["type"] = "grammar"
        return data


class ResumeAnalysisSchema(BaseModel):
    """Full analysis output schema returned by Gemini AI."""
    summary: str = Field(
        validation_alias=AliasChoices("summary", "verdict", "overview", "executive_summary"),
        description="3-4 sentence editorial verdict summarizing the resume's performance"
    )
    overall_score: int = Field(
        ge=0, le=100,
        validation_alias=AliasChoices("overall_score", "score", "total_score"),
        description="Weighted composite score from 0 to 100"
    )
    ats: ATSResult = Field(description="ATS compatibility breakdown")
    job_match: Optional[JobMatchResult] = Field(
        default=None,
        description="Target job match analysis (null if no target role or job description provided)"
    )
    criteria_scores: List[CriterionScore] = Field(description="Scores for the 8 official rubric criteria")
    sections: List[SectionEvaluation] = Field(description="Individual evaluations for each major section")
    strengths: List[str] = Field(default_factory=list, description="Key strengths identified in the resume")
    weaknesses: List[str] = Field(default_factory=list, description="Key weaknesses or gaps in the resume")
    suggestions: List[PrioritizedSuggestion] = Field(default_factory=list, description="Ranked actionable suggestions")
    bullet_rewrites: List[BulletRewrite] = Field(default_factory=list, description="Before/after bullet rewrites with context")
    language_issues: List[LanguageIssue] = Field(default_factory=list, description="Specific language, grammar, or phrasing improvements")

    @model_validator(mode="before")
    @classmethod
    def normalize_llm_json(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # 1. Normalize criteria_scores if returned as a dict {criterion_name: score}
        raw_criteria = data.get("criteria_scores")
        if isinstance(raw_criteria, dict):
            normalized_crit = []
            for k, v in raw_criteria.items():
                clean_name = k.replace("_", " ").title()
                score_val = v.get("score", v) if isinstance(v, dict) else v
                reasoning_val = v.get("reasoning", "") if isinstance(v, dict) else ""
                normalized_crit.append({
                    "name": clean_name,
                    "score": int(score_val) if isinstance(score_val, (int, float)) else 75,
                    "reasoning": str(reasoning_val)
                })
            data["criteria_scores"] = normalized_crit

        # 2. Normalize sections if returned as a dict {section_name: {score: ..., ...}}
        raw_sections = data.get("sections")
        if isinstance(raw_sections, dict):
            normalized_sec = []
            for k, v in raw_sections.items():
                sec_name = k.capitalize()
                if isinstance(v, dict):
                    normalized_sec.append({
                        "name": sec_name,
                        "score": int(v.get("score", 75)),
                        "reasoning": str(v.get("reasoning", "")),
                        "suggestions": v.get("suggestions", [])
                    })
                elif isinstance(v, (int, float)):
                    normalized_sec.append({
                        "name": sec_name,
                        "score": int(v),
                        "reasoning": "",
                        "suggestions": []
                    })
            data["sections"] = normalized_sec

        # 3. Ensure ats is properly formatted
        ats_val = data.get("ats")
        if isinstance(ats_val, (int, float)):
            data["ats"] = {"score": int(ats_val), "checks": []}

        return data
