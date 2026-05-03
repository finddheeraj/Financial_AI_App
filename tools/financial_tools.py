import json
import math
from tools.registry import tool
from utils.currency import format_inr


def _chart_block(chart_type, title, labels, datasets, colors=None):
    chart = {"type": chart_type, "title": title, "labels": labels, "datasets": datasets}
    if colors:
        chart["colors"] = colors
    return f"\n\n[CHART_DATA]\n{json.dumps(chart)}\n[/CHART_DATA]"


@tool(
    name="compound_interest",
    description="Calculate future value of an investment with compound interest and optional monthly contributions.",
    parameters=[
        {"name": "principal", "type": "float", "description": "Initial investment amount in rupees"},
        {"name": "annual_rate", "type": "float", "description": "Annual interest rate as percentage (e.g. 7.0 for 7%)"},
        {"name": "years", "type": "int", "description": "Number of years to invest"},
        {"name": "monthly_contribution", "type": "float", "description": "Monthly contribution amount in rupees", "required": False, "default": 0.0},
    ],
)
def compound_interest(principal: float, annual_rate: float, years: int, monthly_contribution: float = 0.0) -> str:
    r = annual_rate / 100 / 12
    n = years * 12
    if r > 0:
        fv_principal = principal * (1 + r) ** n
        fv_contributions = monthly_contribution * (((1 + r) ** n - 1) / r)
    else:
        fv_principal = principal
        fv_contributions = monthly_contribution * n
    total_fv = fv_principal + fv_contributions
    total_contributed = principal + monthly_contribution * n
    interest_earned = total_fv - total_contributed
    return (
        f"Future Value: {format_inr(total_fv)}\n"
        f"Total Contributed: {format_inr(total_contributed)}\n"
        f"Interest Earned: {format_inr(interest_earned)}\n"
        f"Return on Investment: {(interest_earned / total_contributed * 100) if total_contributed > 0 else 0:.1f}%"
    )


@tool(
    name="budget_analyzer",
    description="Analyze income vs expenses and provide savings rate and 50/30/20 rule assessment.",
    parameters=[
        {"name": "annual_income", "type": "float", "description": "Annual gross income in rupees"},
        {"name": "monthly_expenses", "type": "float", "description": "Total monthly expenses in rupees"},
        {"name": "monthly_debt_payments", "type": "float", "description": "Monthly debt/EMI payments in rupees", "required": False, "default": 0.0},
    ],
)
def budget_analyzer(annual_income: float, monthly_expenses: float, monthly_debt_payments: float = 0.0) -> str:
    monthly_income = annual_income / 12
    total_outflow = monthly_expenses + monthly_debt_payments
    surplus = monthly_income - total_outflow
    savings_rate = (surplus / monthly_income * 100) if monthly_income > 0 else 0
    needs_target = monthly_income * 0.50
    wants_target = monthly_income * 0.30
    savings_target = monthly_income * 0.20
    return (
        f"Monthly Income: {format_inr(monthly_income)}\n"
        f"Monthly Expenses: {format_inr(monthly_expenses)}\n"
        f"Monthly EMI/Debt Payments: {format_inr(monthly_debt_payments)}\n"
        f"Monthly Surplus: {format_inr(surplus)}\n"
        f"Savings Rate: {savings_rate:.1f}%\n"
        f"--- 50/30/20 Rule ---\n"
        f"Needs Budget (50%): {format_inr(needs_target)}\n"
        f"Wants Budget (30%): {format_inr(wants_target)}\n"
        f"Savings/Investment Budget (20%): {format_inr(savings_target)}\n"
        f"Annual Savings Potential: {format_inr(surplus * 12)}"
    ) + _chart_block(
        "pie", "50/30/20 Budget Split",
        ["Needs (50%)", "Wants (30%)", "Savings (20%)"],
        [{"data": [round(needs_target), round(wants_target), round(savings_target)]}],
        colors=["#00AEEF", "#FFBB28", "#00857C"],
    )


@tool(
    name="debt_payoff_timeline",
    description="Calculate how long it takes to pay off a loan/debt and total interest paid.",
    parameters=[
        {"name": "balance", "type": "float", "description": "Current debt/loan balance in rupees"},
        {"name": "annual_rate", "type": "float", "description": "Annual interest rate as percentage (e.g. 9.0 for 9%)"},
        {"name": "monthly_payment", "type": "float", "description": "Monthly EMI/payment amount in rupees"},
    ],
)
def debt_payoff_timeline(balance: float, annual_rate: float, monthly_payment: float) -> str:
    if balance <= 0:
        return "No debt to pay off."
    if monthly_payment <= 0:
        return "Error: Monthly payment must be positive."
    r = annual_rate / 100 / 12
    if r > 0:
        min_payment = balance * r
        if monthly_payment <= min_payment:
            return f"Error: EMI {format_inr(monthly_payment)} does not cover monthly interest {format_inr(min_payment)}. Debt will grow."
        months = -math.log(1 - (r * balance / monthly_payment)) / math.log(1 + r)
    else:
        months = balance / monthly_payment
    months = math.ceil(months)
    total_paid = monthly_payment * months
    total_interest = total_paid - balance
    return (
        f"Months to Payoff: {months} ({months / 12:.1f} years)\n"
        f"Total Amount Paid: {format_inr(total_paid)}\n"
        f"Total Interest Paid: {format_inr(total_interest)}\n"
        f"Interest as % of Principal: {(total_interest / balance * 100):.1f}%"
    )


@tool(
    name="emergency_fund_calculator",
    description="Assess emergency fund adequacy based on monthly expenses and current savings.",
    parameters=[
        {"name": "monthly_expenses", "type": "float", "description": "Total monthly expenses in rupees"},
        {"name": "current_savings", "type": "float", "description": "Current savings/emergency fund in rupees"},
        {"name": "target_months", "type": "int", "description": "Target months of expenses to cover", "required": False, "default": 6},
    ],
)
def emergency_fund_calculator(monthly_expenses: float, current_savings: float, target_months: int = 6) -> str:
    target = monthly_expenses * target_months
    min_target = monthly_expenses * 3
    coverage_months = current_savings / monthly_expenses if monthly_expenses > 0 else 0
    shortfall = max(0, target - current_savings)
    if current_savings >= target:
        status = "EXCELLENT - Fully funded"
    elif current_savings >= min_target:
        status = "GOOD - Meets minimum 3-month threshold"
    else:
        status = "NEEDS ATTENTION - Below minimum"
    return (
        f"Target ({target_months} months): {format_inr(target)}\n"
        f"Minimum (3 months): {format_inr(min_target)}\n"
        f"Current Savings: {format_inr(current_savings)}\n"
        f"Coverage: {coverage_months:.1f} months\n"
        f"Shortfall to Target: {format_inr(shortfall)}\n"
        f"Status: {status}\n"
        f"Tip: Keep emergency fund in liquid funds or savings account for easy access"
    )


@tool(
    name="retirement_projector",
    description="Project retirement savings and check if on track using the 4% withdrawal rule. Uses Indian retirement context (age 60, NPS/EPF).",
    parameters=[
        {"name": "current_age", "type": "int", "description": "Current age in years"},
        {"name": "retirement_age", "type": "int", "description": "Target retirement age (typical in India: 60)"},
        {"name": "current_savings", "type": "float", "description": "Current total retirement savings in rupees (EPF + NPS + other)"},
        {"name": "monthly_contribution", "type": "float", "description": "Monthly retirement contribution in rupees"},
        {"name": "annual_return", "type": "float", "description": "Expected annual return as percentage", "required": False, "default": 10.0},
    ],
)
def retirement_projector(
    current_age: int, retirement_age: int, current_savings: float,
    monthly_contribution: float, annual_return: float = 10.0,
) -> str:
    years = retirement_age - current_age
    if years <= 0:
        return "Error: Retirement age must be greater than current age."
    r = annual_return / 100 / 12
    n = years * 12
    if r > 0:
        fv = current_savings * (1 + r) ** n + monthly_contribution * (((1 + r) ** n - 1) / r)
    else:
        fv = current_savings + monthly_contribution * n
    annual_withdrawal = fv * 0.04
    monthly_withdrawal = annual_withdrawal / 12

    chart_labels = []
    chart_contributed = []
    chart_corpus = []
    for y in range(1, years + 1):
        m = y * 12
        cont = current_savings + monthly_contribution * m
        if r > 0:
            corpus = current_savings * (1 + r) ** m + monthly_contribution * (((1 + r) ** m - 1) / r)
        else:
            corpus = cont
        chart_labels.append(f"Age {current_age + y}")
        chart_contributed.append(round(cont))
        chart_corpus.append(round(corpus))

    return (
        f"Years to Retirement: {years}\n"
        f"Projected Corpus at Age {retirement_age}: {format_inr(fv)}\n"
        f"Safe Annual Withdrawal (4% rule): {format_inr(annual_withdrawal)}\n"
        f"Safe Monthly Withdrawal: {format_inr(monthly_withdrawal)}\n"
        f"Total Contributed: {format_inr(current_savings + monthly_contribution * n)}\n"
        f"--- India Retirement Context ---\n"
        f"Consider: EPF (employer match), NPS (tax benefit under 80CCD(1B)), PPF (7.1% tax-free)\n"
        f"NPS: At 60, min 40% must buy annuity, rest is tax-free lump sum\n"
        f"EPF: Full withdrawal at 58, partial at 55 with conditions"
    ) + _chart_block(
        "line", "Retirement Corpus Projection",
        chart_labels,
        [
            {"label": "Total Contributed", "data": chart_contributed},
            {"label": "Projected Corpus", "data": chart_corpus},
        ],
    )


@tool(
    name="asset_allocation",
    description="Recommend portfolio asset allocation with Indian investment vehicles based on risk tolerance and time horizon.",
    parameters=[
        {"name": "risk_tolerance", "type": "str", "description": "Risk tolerance: conservative, moderate, or aggressive"},
        {"name": "time_horizon_years", "type": "int", "description": "Investment time horizon in years"},
        {"name": "total_investable", "type": "float", "description": "Total investable amount in rupees"},
    ],
)
def asset_allocation(risk_tolerance: str, time_horizon_years: int, total_investable: float) -> str:
    base_equity = min(90, max(20, 50 + time_horizon_years))
    adjustments = {"conservative": -20, "moderate": 0, "aggressive": 15}
    adj = adjustments.get(risk_tolerance.lower(), 0)
    equity_pct = min(90, max(20, base_equity + adj))
    fixed_pct = 100 - equity_pct

    large_cap = round(equity_pct * 0.40)
    mid_cap = round(equity_pct * 0.25)
    small_cap = round(equity_pct * 0.15)
    intl_mf = round(equity_pct * 0.10)
    reits = equity_pct - large_cap - mid_cap - small_cap - intl_mf

    ppf_epf = round(fixed_pct * 0.30)
    debt_mf = round(fixed_pct * 0.25)
    nps = round(fixed_pct * 0.20)
    sgb = round(fixed_pct * 0.15)
    fd_corp = fixed_pct - ppf_epf - debt_mf - nps - sgb

    return (
        f"Recommended Allocation ({risk_tolerance}, {time_horizon_years}yr horizon):\n"
        f"  Equity: {equity_pct}% ({format_inr(total_investable * equity_pct / 100)})\n"
        f"    - Large Cap MFs: {large_cap}%\n"
        f"    - Mid Cap MFs: {mid_cap}%\n"
        f"    - Small Cap MFs: {small_cap}%\n"
        f"    - International MFs: {intl_mf}%\n"
        f"    - REITs: {reits}%\n"
        f"  Fixed Income: {fixed_pct}% ({format_inr(total_investable * fixed_pct / 100)})\n"
        f"    - PPF/EPF: {ppf_epf}% (tax-free, guaranteed)\n"
        f"    - Debt Mutual Funds: {debt_mf}%\n"
        f"    - NPS (Tier 1): {nps}% (tax benefit + pension)\n"
        f"    - Sovereign Gold Bonds: {sgb}% (gold + 2.5% interest)\n"
        f"    - FD/Corporate Bonds: {fd_corp}%\n"
        f"  Rebalance: {'Quarterly' if risk_tolerance == 'aggressive' else 'Semi-annually'}"
    ) + _chart_block(
        "pie", "Portfolio Allocation",
        ["Large Cap MF", "Mid Cap MF", "Small Cap MF", "Intl MF", "REITs",
         "PPF/EPF", "Debt MF", "NPS", "Gold Bonds", "FD/Bonds"],
        [{"data": [large_cap, mid_cap, small_cap, intl_mf, reits, ppf_epf, debt_mf, nps, sgb, fd_corp]}],
    )


@tool(
    name="goal_feasibility",
    description="Analyze whether a specific savings goal is achievable and calculate the required monthly SIP.",
    parameters=[
        {"name": "goal_amount", "type": "float", "description": "Target goal amount in rupees"},
        {"name": "current_savings", "type": "float", "description": "Current savings toward this goal in rupees"},
        {"name": "monthly_contribution", "type": "float", "description": "Planned monthly SIP/contribution in rupees"},
        {"name": "years", "type": "int", "description": "Time frame in years to reach the goal"},
        {"name": "annual_return", "type": "float", "description": "Expected annual return as percentage", "required": False, "default": 10.0},
    ],
)
def goal_feasibility(
    goal_amount: float, current_savings: float, monthly_contribution: float,
    years: int, annual_return: float = 10.0,
) -> str:
    r = annual_return / 100 / 12
    n = years * 12
    if r > 0:
        projected = current_savings * (1 + r) ** n + monthly_contribution * (((1 + r) ** n - 1) / r)
    else:
        projected = current_savings + monthly_contribution * n
    gap = goal_amount - projected
    if gap > 0 and r > 0:
        required_monthly = gap / (((1 + r) ** n - 1) / r)
    elif gap > 0:
        required_monthly = gap / n
    else:
        required_monthly = 0
    feasible = projected >= goal_amount
    return (
        f"Goal Amount: {format_inr(goal_amount)}\n"
        f"Projected Amount: {format_inr(projected)}\n"
        f"{'Surplus' if feasible else 'Shortfall'}: {format_inr(abs(gap))}\n"
        f"Feasible: {'YES' if feasible else 'NO'}\n"
        f"Additional Monthly SIP Needed: {format_inr(required_monthly)}\n"
        f"Confidence: {'High' if projected >= goal_amount * 1.1 else 'Moderate' if feasible else 'Low'}"
    )


# --- India-Specific Tools ---


@tool(
    name="income_tax_calculator",
    description="Calculate Indian income tax under both Old and New regimes (FY 2024-25), compare them, and recommend which regime saves more tax.",
    parameters=[
        {"name": "annual_income", "type": "float", "description": "Annual gross income in rupees"},
        {"name": "hra_received", "type": "float", "description": "Annual HRA received in rupees", "required": False, "default": 0.0},
        {"name": "rent_paid", "type": "float", "description": "Annual rent paid in rupees", "required": False, "default": 0.0},
        {"name": "section_80c", "type": "float", "description": "Total 80C investments (PPF+ELSS+EPF+LIC etc) in rupees, max 1.5 lakh", "required": False, "default": 0.0},
        {"name": "section_80d", "type": "float", "description": "Health insurance premium under 80D in rupees", "required": False, "default": 0.0},
        {"name": "metro_city", "type": "str", "description": "Metro city for HRA: 'yes' or 'no'", "required": False, "default": "yes"},
    ],
)
def income_tax_calculator(
    annual_income: float, hra_received: float = 0.0, rent_paid: float = 0.0,
    section_80c: float = 0.0, section_80d: float = 0.0, metro_city: str = "yes",
) -> str:
    basic_salary = annual_income * 0.40

    # --- Old Regime ---
    old_standard_deduction = min(50_000, annual_income)
    hra_exempt = 0.0
    if hra_received > 0 and rent_paid > 0:
        metro_pct = 0.50 if metro_city.lower() == "yes" else 0.40
        hra_exempt = min(
            hra_received,
            metro_pct * basic_salary,
            max(0, rent_paid - 0.10 * basic_salary),
        )
    actual_80c = min(section_80c, 1_50_000)
    actual_80d = min(section_80d, 25_000)
    old_taxable = max(0, annual_income - old_standard_deduction - hra_exempt - actual_80c - actual_80d)

    def _calc_old_tax(taxable):
        if taxable <= 2_50_000:
            return 0
        tax = 0
        if taxable > 10_00_000:
            tax += (taxable - 10_00_000) * 0.30
            taxable = 10_00_000
        if taxable > 5_00_000:
            tax += (taxable - 5_00_000) * 0.20
            taxable = 5_00_000
        if taxable > 2_50_000:
            tax += (taxable - 2_50_000) * 0.05
        return tax

    old_tax = _calc_old_tax(old_taxable)
    if old_taxable <= 5_00_000:
        old_tax = 0
    old_cess = old_tax * 0.04
    old_total = old_tax + old_cess

    # --- New Regime ---
    new_standard_deduction = min(75_000, annual_income)
    new_taxable = max(0, annual_income - new_standard_deduction)

    def _calc_new_tax(taxable):
        if taxable <= 3_00_000:
            return 0
        tax = 0
        slabs = [
            (3_00_000, 7_00_000, 0.05),
            (7_00_000, 10_00_000, 0.10),
            (10_00_000, 12_00_000, 0.15),
            (12_00_000, 15_00_000, 0.20),
            (15_00_000, float("inf"), 0.30),
        ]
        for lower, upper, rate in slabs:
            if taxable > lower:
                tax += (min(taxable, upper) - lower) * rate
        return tax

    new_tax = _calc_new_tax(new_taxable)
    if new_taxable <= 7_00_000:
        new_tax = 0
    new_cess = new_tax * 0.04
    new_total = new_tax + new_cess

    # --- Comparison ---
    diff = old_total - new_total
    better = "New" if new_total <= old_total else "Old"
    old_effective = (old_total / annual_income * 100) if annual_income > 0 else 0
    new_effective = (new_total / annual_income * 100) if annual_income > 0 else 0

    return (
        f"--- OLD REGIME ---\n"
        f"Gross Income: {format_inr(annual_income)}\n"
        f"Standard Deduction: {format_inr(old_standard_deduction)}\n"
        f"HRA Exemption: {format_inr(hra_exempt)}\n"
        f"Section 80C: {format_inr(actual_80c)}\n"
        f"Section 80D: {format_inr(actual_80d)}\n"
        f"Taxable Income: {format_inr(old_taxable)}\n"
        f"Tax + Cess (4%): {format_inr(old_total)}\n"
        f"\n--- NEW REGIME ---\n"
        f"Gross Income: {format_inr(annual_income)}\n"
        f"Standard Deduction: {format_inr(new_standard_deduction)}\n"
        f"Taxable Income: {format_inr(new_taxable)}\n"
        f"Tax + Cess (4%): {format_inr(new_total)}\n"
        f"\n--- COMPARISON ---\n"
        f"Old Regime Tax: {format_inr(old_total)} (effective {old_effective:.1f}%)\n"
        f"New Regime Tax: {format_inr(new_total)} (effective {new_effective:.1f}%)\n"
        f"Savings with {better} Regime: {format_inr(abs(diff))}\n"
        f"Recommendation: {better} Regime is better for you"
    ) + _chart_block(
        "bar", "Tax: Old vs New Regime",
        ["Old Regime", "New Regime"],
        [{"label": "Total Tax + Cess", "data": [round(old_total), round(new_total)]}],
        colors=["#00857C", "#FF5722"],
    )


@tool(
    name="section_80c_planner",
    description="Plan optimal Section 80C (limit 1.5 lakh) allocation across PPF, ELSS, NPS, EPF, Tax Saving FD. Also covers 80CCD(1B) extra 50k for NPS.",
    parameters=[
        {"name": "available_amount", "type": "float", "description": "Amount available to invest under 80C in rupees (max 1,50,000)"},
        {"name": "risk_tolerance", "type": "str", "description": "Risk tolerance: conservative, moderate, or aggressive"},
        {"name": "epf_contribution", "type": "float", "description": "Annual employee EPF contribution already made in rupees", "required": False, "default": 0.0},
    ],
)
def section_80c_planner(available_amount: float, risk_tolerance: str, epf_contribution: float = 0.0) -> str:
    limit = 1_50_000
    capped = min(available_amount, limit)
    remaining = max(0, capped - epf_contribution)

    if remaining <= 0:
        return (
            f"Your EPF contribution ({format_inr(epf_contribution)}) already covers the full 80C limit of {format_inr(limit)}.\n"
            f"Consider NPS under 80CCD(1B) for additional {format_inr(50_000)} tax benefit."
        )

    allocations = {
        "conservative": {"ppf": 0.50, "elss": 0.20, "fd": 0.30},
        "moderate": {"ppf": 0.35, "elss": 0.40, "fd": 0.25},
        "aggressive": {"ppf": 0.20, "elss": 0.60, "fd": 0.20},
    }
    alloc = allocations.get(risk_tolerance.lower(), allocations["moderate"])
    ppf = remaining * alloc["ppf"]
    elss = remaining * alloc["elss"]
    fd = remaining * alloc["fd"]
    nps_extra = 50_000
    total_deduction = capped + nps_extra
    tax_saved_30 = total_deduction * 0.312

    return (
        f"--- 80C Allocation (Limit: {format_inr(limit)}) ---\n"
        f"EPF (already invested): {format_inr(epf_contribution)}\n"
        f"Remaining 80C Capacity: {format_inr(remaining)}\n"
        f"\nRecommended Allocation ({risk_tolerance}):\n"
        f"  PPF: {format_inr(ppf)} — 7.1% tax-free, 15yr lock-in\n"
        f"  ELSS: {format_inr(elss)} — Equity MF, 3yr lock-in, market-linked\n"
        f"  Tax Saving FD: {format_inr(fd)} — ~7% interest, 5yr lock-in\n"
        f"\n--- Beyond 80C: 80CCD(1B) ---\n"
        f"  NPS Tier 1: {format_inr(nps_extra)} extra deduction\n"
        f"\nTotal Tax Deduction: {format_inr(total_deduction)}\n"
        f"Estimated Tax Saved (30% slab + cess): {format_inr(tax_saved_30)}"
    ) + _chart_block(
        "pie", "80C + 80CCD(1B) Allocation",
        ["EPF", "PPF", "ELSS", "Tax Saving FD", "NPS (80CCD)"],
        [{"data": [round(epf_contribution), round(ppf), round(elss), round(fd), round(nps_extra)]}],
        colors=["#003D6B", "#00AEEF", "#00857C", "#FFBB28", "#8884D8"],
    )


@tool(
    name="sip_calculator",
    description="Calculate SIP (Systematic Investment Plan) returns for Indian mutual funds with monthly investment projections.",
    parameters=[
        {"name": "monthly_sip", "type": "float", "description": "Monthly SIP amount in rupees"},
        {"name": "annual_return", "type": "float", "description": "Expected annual return as percentage (e.g. 12.0 for 12%)"},
        {"name": "years", "type": "int", "description": "Investment duration in years"},
    ],
)
def sip_calculator(monthly_sip: float, annual_return: float, years: int) -> str:
    r = annual_return / 100 / 12
    n = years * 12
    if r > 0:
        fv = monthly_sip * (((1 + r) ** n - 1) / r) * (1 + r)
    else:
        fv = monthly_sip * n
    total_invested = monthly_sip * n
    wealth_gained = fv - total_invested

    milestones = []
    for y in [max(1, years // 4), max(1, years // 2), max(1, years * 3 // 4), years]:
        m = y * 12
        if r > 0:
            val = monthly_sip * (((1 + r) ** m - 1) / r) * (1 + r)
        else:
            val = monthly_sip * m
        milestones.append((y, monthly_sip * m, val))

    result = (
        f"--- SIP Investment Summary ---\n"
        f"Monthly SIP: {format_inr(monthly_sip)}\n"
        f"Duration: {years} years ({n} months)\n"
        f"Expected Annual Return: {annual_return}%\n"
        f"\nTotal Amount Invested: {format_inr(total_invested)}\n"
        f"Expected Corpus: {format_inr(fv)}\n"
        f"Wealth Gained: {format_inr(wealth_gained)}\n"
        f"Returns Multiple: {fv / total_invested:.1f}x\n"
        f"\n--- Year-wise Milestones ---\n"
    )
    for y, invested, value in milestones:
        result += f"  Year {y}: Invested {format_inr(invested)} -> Value {format_inr(value)}\n"

    chart_labels = []
    chart_invested = []
    chart_values = []
    for y in range(1, years + 1):
        m = y * 12
        inv = monthly_sip * m
        if r > 0:
            val = monthly_sip * (((1 + r) ** m - 1) / r) * (1 + r)
        else:
            val = inv
        chart_labels.append(f"Yr {y}")
        chart_invested.append(round(inv))
        chart_values.append(round(val))

    return result + _chart_block(
        "line", "SIP Growth Over Time",
        chart_labels,
        [
            {"label": "Amount Invested", "data": chart_invested},
            {"label": "Corpus Value", "data": chart_values},
        ],
    )
