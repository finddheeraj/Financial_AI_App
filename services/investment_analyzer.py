from models.schemas import UserProfile, AdvisorResponse
from prompts.templates import (
    SYSTEM_PROMPT,
    INVESTMENT_PROMPT,
    build_profile_summary,
)
from services.llm_service import generate


def get_investment_insights(profile: UserProfile) -> AdvisorResponse:
    summary = build_profile_summary(profile)
    prompt = INVESTMENT_PROMPT.format(
        system=SYSTEM_PROMPT,
        profile_summary=summary,
        risk_tolerance=profile.risk_tolerance,
    )
    advice = generate(prompt)
    return AdvisorResponse(
        category="Investment Insights",
        advice=advice,
        profile_summary=summary,
    )
