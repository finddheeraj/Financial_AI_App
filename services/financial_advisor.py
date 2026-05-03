from models.schemas import UserProfile, AdvisorResponse
from prompts.templates import (
    SYSTEM_PROMPT,
    RECOMMENDATION_PROMPT,
    CUSTOM_QUESTION_PROMPT,
    build_profile_summary,
)
from services.llm_service import generate


def get_recommendations(profile: UserProfile) -> AdvisorResponse:
    summary = build_profile_summary(profile)
    prompt = RECOMMENDATION_PROMPT.format(
        system=SYSTEM_PROMPT,
        profile_summary=summary,
    )
    advice = generate(prompt)
    return AdvisorResponse(
        category="Financial Recommendations",
        advice=advice,
        profile_summary=summary,
    )


def ask_question(profile: UserProfile, question: str) -> AdvisorResponse:
    summary = build_profile_summary(profile)
    prompt = CUSTOM_QUESTION_PROMPT.format(
        system=SYSTEM_PROMPT,
        profile_summary=summary,
        question=question,
    )
    advice = generate(prompt)
    return AdvisorResponse(
        category="Custom Question",
        advice=advice,
        profile_summary=summary,
    )
