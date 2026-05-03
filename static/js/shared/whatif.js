import { formatINR } from "./charts.js";
import { simulateSIP, simulateRetirement, simulateTax } from "./simulators.js";

function readProfile() {
    const val = (id, fallback = 0) => parseFloat(document.getElementById(id)?.value) || fallback;
    const income = val("annual_income");
    const expenses = val("monthly_expenses");
    const surplus = Math.max(0, income / 12 - expenses);
    return {
        income,
        expenses,
        surplus,
        savings: val("current_savings"),
        investments: val("current_investments"),
        age: parseInt(document.getElementById("age")?.value) || 30,
        timeHorizon: parseInt(document.getElementById("time_horizon_years")?.value) || 10,
        epfMonthly: val("epf_monthly"),
        hraMonthly: val("hra_monthly"),
        rentMonthly: val("rent_monthly"),
        metroCity: document.getElementById("metro_city")?.value === "true",
    };
}

function fmtCurrency(v) { return formatINR(v); }
function fmtPct(v) { return v + "%"; }
function fmtYears(v) { return v + " yrs"; }
function fmtAge(v) { return "Age " + v; }

function buildSlider(cfg) {
    const row = document.createElement("div");
    row.className = "whatif-row";

    const label = document.createElement("span");
    label.className = "whatif-label";
    label.textContent = cfg.label;

    const valueDisplay = document.createElement("span");
    valueDisplay.className = "whatif-value";
    valueDisplay.textContent = cfg.format(cfg.value);

    const input = document.createElement("input");
    input.type = "range";
    input.min = cfg.min;
    input.max = cfg.max;
    input.step = cfg.step;
    input.value = cfg.value;
    input.className = "whatif-slider";

    input.addEventListener("input", () => {
        const v = parseFloat(input.value);
        valueDisplay.textContent = cfg.format(v);
        cfg.onChange(v);
    });

    row.appendChild(label);
    row.appendChild(valueDisplay);
    row.appendChild(input);
    return row;
}

function updateChart(chart, result) {
    chart.data.labels = result.labels;
    result.datasets.forEach((ds, i) => {
        if (chart.data.datasets[i]) {
            chart.data.datasets[i].data = ds.data;
        }
    });
    chart.update("none");
}

function attachSIPPanel(wrapper, chart) {
    const p = readProfile();
    const state = {
        monthlySip: Math.max(1000, Math.round(p.surplus * 0.5)),
        annualReturn: 12.0,
        years: p.timeHorizon,
    };

    function recalc() { updateChart(chart, simulateSIP(state.monthlySip, state.annualReturn, state.years)); }

    const panel = document.createElement("div");
    panel.className = "whatif-panel";

    const title = document.createElement("div");
    title.className = "whatif-title";
    title.textContent = "Adjust Parameters";
    panel.appendChild(title);

    panel.appendChild(buildSlider({
        label: "Monthly SIP", value: state.monthlySip, min: 500, max: 200000, step: 500,
        format: fmtCurrency, onChange: v => { state.monthlySip = v; recalc(); },
    }));
    panel.appendChild(buildSlider({
        label: "Annual Return", value: state.annualReturn, min: 4, max: 25, step: 0.5,
        format: fmtPct, onChange: v => { state.annualReturn = v; recalc(); },
    }));
    panel.appendChild(buildSlider({
        label: "Years", value: state.years, min: 1, max: 40, step: 1,
        format: fmtYears, onChange: v => { state.years = v; recalc(); },
    }));

    wrapper.appendChild(panel);
}

function attachRetirementPanel(wrapper, chart) {
    const p = readProfile();
    const state = {
        currentAge: p.age,
        retirementAge: 60,
        currentSavings: p.savings + p.investments,
        monthlyContribution: Math.max(0, Math.round(p.surplus * 0.3)),
        annualReturn: 10.0,
    };

    function recalc() {
        updateChart(chart, simulateRetirement(
            state.currentAge, state.retirementAge, state.currentSavings,
            state.monthlyContribution, state.annualReturn,
        ));
    }

    const panel = document.createElement("div");
    panel.className = "whatif-panel";

    const title = document.createElement("div");
    title.className = "whatif-title";
    title.textContent = "Adjust Parameters";
    panel.appendChild(title);

    panel.appendChild(buildSlider({
        label: "Monthly Contribution", value: state.monthlyContribution, min: 500, max: 100000, step: 500,
        format: fmtCurrency, onChange: v => { state.monthlyContribution = v; recalc(); },
    }));
    panel.appendChild(buildSlider({
        label: "Annual Return", value: state.annualReturn, min: 4, max: 15, step: 0.5,
        format: fmtPct, onChange: v => { state.annualReturn = v; recalc(); },
    }));
    panel.appendChild(buildSlider({
        label: "Retirement Age", value: state.retirementAge, min: 45, max: 70, step: 1,
        format: fmtAge, onChange: v => { state.retirementAge = v; recalc(); },
    }));

    wrapper.appendChild(panel);
}

function attachTaxPanel(wrapper, chart) {
    const p = readProfile();
    const state = {
        annualIncome: p.income,
        section80c: Math.min(150000, p.epfMonthly * 12),
        section80d: 25000,
        hraReceived: p.hraMonthly * 12,
        rentPaid: p.rentMonthly * 12,
        metroCity: p.metroCity,
    };

    function recalc() {
        updateChart(chart, simulateTax(
            state.annualIncome, state.section80c, state.section80d,
            state.hraReceived, state.rentPaid, state.metroCity,
        ));
    }

    const panel = document.createElement("div");
    panel.className = "whatif-panel";

    const title = document.createElement("div");
    title.className = "whatif-title";
    title.textContent = "Adjust Parameters";
    panel.appendChild(title);

    panel.appendChild(buildSlider({
        label: "Annual Income", value: state.annualIncome, min: 100000, max: 10000000, step: 50000,
        format: fmtCurrency, onChange: v => { state.annualIncome = v; recalc(); },
    }));
    panel.appendChild(buildSlider({
        label: "80C Investments", value: state.section80c, min: 0, max: 150000, step: 5000,
        format: fmtCurrency, onChange: v => { state.section80c = v; recalc(); },
    }));
    panel.appendChild(buildSlider({
        label: "80D Premium", value: state.section80d, min: 0, max: 50000, step: 1000,
        format: fmtCurrency, onChange: v => { state.section80d = v; recalc(); },
    }));

    wrapper.appendChild(panel);
}

export function attachWhatIfPanels(container, chartInstances, chartDataArray) {
    const wrappers = container.querySelectorAll(".chart-wrapper");

    chartDataArray.forEach((chartData, i) => {
        const chart = chartInstances[i];
        const wrapper = wrappers[i];
        if (!chart || !wrapper) return;

        const title = (chartData.title || "").toLowerCase();

        if (title.includes("sip growth")) {
            attachSIPPanel(wrapper, chart);
        } else if (title.includes("retirement corpus")) {
            attachRetirementPanel(wrapper, chart);
        } else if (title.includes("tax") && title.includes("old vs new")) {
            attachTaxPanel(wrapper, chart);
        }
    });
}
