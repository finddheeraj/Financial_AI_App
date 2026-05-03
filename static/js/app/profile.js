export function getProfile() {
    const splitTrim = v => v ? v.split(",").map(s => s.trim()).filter(Boolean) : [];
    return {
        profile: {
            name: document.getElementById("name").value,
            age: parseInt(document.getElementById("age").value),
            annual_income: parseFloat(document.getElementById("annual_income").value),
            monthly_expenses: parseFloat(document.getElementById("monthly_expenses").value),
            current_savings: parseFloat(document.getElementById("current_savings").value),
            current_investments: parseFloat(document.getElementById("current_investments").value) || 0,
            debt: parseFloat(document.getElementById("debt").value) || 0,
            risk_tolerance: document.getElementById("risk_tolerance").value,
            time_horizon_years: parseInt(document.getElementById("time_horizon_years").value),
            financial_goals: splitTrim(document.getElementById("financial_goals").value),
            investment_preferences: splitTrim(document.getElementById("investment_preferences").value),
            epf_monthly: parseFloat(document.getElementById("epf_monthly").value) || 0,
            hra_monthly: parseFloat(document.getElementById("hra_monthly").value) || 0,
            rent_monthly: parseFloat(document.getElementById("rent_monthly").value) || 0,
            metro_city: document.getElementById("metro_city").value === "true",
        }
    };
}
