from utils.currency import format_inr

SYSTEM_PROMPT = (
    "You are a knowledgeable Indian financial advisor AI. Provide clear, actionable, "
    "and personalized financial guidance for the Indian context. Always include specific "
    "numbers in rupees using Indian notation (lakhs/crores). Reference Indian tax laws "
    "(Section 80C, 80D, HRA), Indian investment vehicles (PPF, NPS, ELSS, SIPs, SGBs), "
    "and Indian retirement norms (retirement at 60, EPF, NPS). Remind the user that this "
    "is educational guidance, not SEBI/AMFI registered professional financial advice."
)


def build_profile_summary(profile) -> str:
    goals = ", ".join(profile.financial_goals) if profile.financial_goals else "Not specified"
    preferences = ", ".join(profile.investment_preferences) if profile.investment_preferences else "Not specified"
    monthly_savings = (profile.annual_income / 12) - profile.monthly_expenses
    savings_rate = (monthly_savings / (profile.annual_income / 12) * 100) if profile.annual_income > 0 else 0

    summary = (
        f"Name: {profile.name}\n"
        f"Age: {profile.age}\n"
        f"Annual Income: {format_inr(profile.annual_income)}\n"
        f"Monthly Expenses: {format_inr(profile.monthly_expenses)}\n"
        f"Monthly Savings Capacity: {format_inr(monthly_savings)} ({savings_rate:.1f}% savings rate)\n"
        f"Current Savings: {format_inr(profile.current_savings)}\n"
        f"Current Investments: {format_inr(profile.current_investments)}\n"
        f"Debt: {format_inr(profile.debt)}\n"
        f"Risk Tolerance: {profile.risk_tolerance}\n"
        f"Time Horizon: {profile.time_horizon_years} years\n"
        f"Financial Goals: {goals}\n"
        f"Investment Preferences: {preferences}"
    )

    if getattr(profile, "epf_monthly", 0) > 0:
        summary += f"\nMonthly EPF Contribution: {format_inr(profile.epf_monthly)}"
    if getattr(profile, "hra_monthly", 0) > 0:
        summary += f"\nMonthly HRA Received: {format_inr(profile.hra_monthly)}"
    if getattr(profile, "rent_monthly", 0) > 0:
        summary += f"\nMonthly Rent Paid: {format_inr(profile.rent_monthly)}"
    if hasattr(profile, "metro_city"):
        summary += f"\nCity: {'Metro' if profile.metro_city else 'Non-Metro'}"

    return summary


RECOMMENDATION_PROMPT = """{system}

Based on this client profile:
{profile_summary}

Provide personalized financial recommendations covering:
1. Budget optimization based on their income and expenses
2. Debt management strategy (if applicable)
3. Emergency fund assessment
4. Section 80C/80D tax-saving targets and regime choice (old vs new)
5. Key action items to improve their financial position

Be specific with rupee amounts and percentages. Keep the advice practical and actionable."""


INVESTMENT_PROMPT = """{system}

Based on this investor profile:
{profile_summary}

Provide investment insights covering:
1. Recommended asset allocation based on risk tolerance and time horizon
2. Specific investment suggestions (SIP mutual funds, PPF, NPS, ELSS, SGBs, debt funds)
3. Diversification strategy across equity and fixed income
4. SIP (Systematic Investment Plan) strategy and recommended amounts
5. Tax-efficient approaches (ELSS for 80C, debt fund indexation, LTCG harvesting)

Include specific allocation percentages in rupees. Tailor to their risk tolerance: {risk_tolerance}."""


PLANNING_PROMPT = """{system}

Based on this client profile:
{profile_summary}

Create a comprehensive financial plan covering:
1. Short-term plan (next 12 months) with monthly milestones
2. Medium-term plan (1-5 years) with quarterly targets
3. Long-term plan (5+ years) with annual projections
4. Retirement planning (EPF, NPS, PPF contributions)
5. Tax planning (80C optimization, old vs new regime, HRA)

Use specific rupee amounts with Indian notation (lakhs/crores). Align the plan with their stated goals: {goals}."""


CUSTOM_QUESTION_PROMPT = """{system}

Client profile:
{profile_summary}

The client asks: {question}

Provide a thorough, personalized answer based on their financial profile."""
