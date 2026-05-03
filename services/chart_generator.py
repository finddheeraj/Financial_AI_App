import json
import re

from models.schemas import UserProfile
from tools.registry import execute_tool


def _extract_charts(tool_output):
    charts = []
    for match in re.finditer(r'\[CHART_DATA\](.*?)\[/CHART_DATA\]', tool_output, re.DOTALL):
        try:
            charts.append(json.loads(match.group(1).strip()))
        except (json.JSONDecodeError, ValueError):
            pass
    return charts


def _run_tool(name, args):
    result = execute_tool(name, args)
    return _extract_charts(result)


def charts_for_recommendations(profile: UserProfile):
    charts = []
    charts += _run_tool("budget_analyzer", {
        "annual_income": profile.annual_income,
        "monthly_expenses": profile.monthly_expenses,
        "monthly_debt_payments": 0,
    })
    charts += _run_tool("emergency_fund_calculator", {
        "monthly_expenses": profile.monthly_expenses,
        "current_savings": profile.current_savings,
    })
    charts += _run_tool("asset_allocation", {
        "risk_tolerance": profile.risk_tolerance,
        "time_horizon_years": profile.time_horizon_years,
        "total_investable": profile.current_investments + profile.current_savings,
    })
    return charts


def charts_for_investment_insights(profile: UserProfile):
    charts = []
    charts += _run_tool("asset_allocation", {
        "risk_tolerance": profile.risk_tolerance,
        "time_horizon_years": profile.time_horizon_years,
        "total_investable": profile.current_investments + profile.current_savings,
    })
    charts += _run_tool("sip_calculator", {
        "monthly_sip": max(1000, (profile.annual_income / 12 - profile.monthly_expenses) * 0.5),
        "annual_return": 12.0,
        "years": profile.time_horizon_years,
    })
    return charts


def charts_for_financial_plan(profile: UserProfile):
    charts = []
    charts += _run_tool("budget_analyzer", {
        "annual_income": profile.annual_income,
        "monthly_expenses": profile.monthly_expenses,
        "monthly_debt_payments": 0,
    })
    charts += _run_tool("income_tax_calculator", {
        "annual_income": profile.annual_income,
        "hra_received": profile.hra_monthly * 12,
        "rent_paid": profile.rent_monthly * 12,
        "section_80c": min(150000, profile.epf_monthly * 12),
        "section_80d": 25000,
        "metro_city": "yes" if profile.metro_city else "no",
    })
    charts += _run_tool("retirement_projector", {
        "current_age": profile.age,
        "retirement_age": 60,
        "current_savings": profile.current_savings + profile.current_investments,
        "monthly_contribution": max(0, profile.annual_income / 12 - profile.monthly_expenses) * 0.3,
        "annual_return": 10.0,
    })
    charts += _run_tool("section_80c_planner", {
        "available_amount": 150000,
        "risk_tolerance": profile.risk_tolerance,
        "epf_contribution": profile.epf_monthly * 12,
    })
    return charts
