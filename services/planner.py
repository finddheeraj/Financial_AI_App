from models.schemas import UserProfile, AdvisorResponse
from prompts.templates import (
    SYSTEM_PROMPT,
    PLANNING_PROMPT,
    build_profile_summary,
)
from services.llm_service import generate, generate_stream


def get_financial_plan(profile: UserProfile) -> AdvisorResponse:
    summary = build_profile_summary(profile)
    goals = ", ".join(profile.financial_goals) if profile.financial_goals else "General financial wellness"
    prompt = PLANNING_PROMPT.format(
        system=SYSTEM_PROMPT,
        profile_summary=summary,
        goals=goals,
    )
    advice = generate(prompt)
    return AdvisorResponse(
        category="Financial Plan",
        advice=advice,
        profile_summary=summary,
    )


def stream_financial_plan(profile: UserProfile):
    summary = build_profile_summary(profile)
    goals = ", ".join(profile.financial_goals) if profile.financial_goals else "General financial wellness"
    prompt = PLANNING_PROMPT.format(
        system=SYSTEM_PROMPT,
        profile_summary=summary,
        goals=goals,
    )
    yield from generate_stream(prompt)
