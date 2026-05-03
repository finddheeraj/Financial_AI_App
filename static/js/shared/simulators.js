export function simulateSIP(monthlySip, annualReturn, years) {
    const r = annualReturn / 100 / 12;
    const labels = [];
    const invested = [];
    const corpus = [];

    for (let y = 1; y <= years; y++) {
        const m = y * 12;
        const inv = monthlySip * m;
        let val;
        if (r > 0) {
            val = monthlySip * (((1 + r) ** m - 1) / r) * (1 + r);
        } else {
            val = inv;
        }
        labels.push(`Yr ${y}`);
        invested.push(Math.round(inv));
        corpus.push(Math.round(val));
    }

    return {
        labels,
        datasets: [
            { label: "Amount Invested", data: invested },
            { label: "Corpus Value", data: corpus },
        ],
    };
}

export function simulateRetirement(currentAge, retirementAge, currentSavings, monthlyContribution, annualReturn) {
    const years = retirementAge - currentAge;
    if (years <= 0) return { labels: [], datasets: [{ label: "Total Contributed", data: [] }, { label: "Projected Corpus", data: [] }] };

    const r = annualReturn / 100 / 12;
    const labels = [];
    const contributed = [];
    const corpusData = [];

    for (let y = 1; y <= years; y++) {
        const m = y * 12;
        const cont = currentSavings + monthlyContribution * m;
        let corp;
        if (r > 0) {
            corp = currentSavings * (1 + r) ** m + monthlyContribution * (((1 + r) ** m - 1) / r);
        } else {
            corp = cont;
        }
        labels.push(`Age ${currentAge + y}`);
        contributed.push(Math.round(cont));
        corpusData.push(Math.round(corp));
    }

    return {
        labels,
        datasets: [
            { label: "Total Contributed", data: contributed },
            { label: "Projected Corpus", data: corpusData },
        ],
    };
}

export function simulateTax(annualIncome, section80c, section80d, hraReceived, rentPaid, metroCity) {
    const basicSalary = annualIncome * 0.40;

    // Old regime
    const oldStdDeduction = Math.min(50000, annualIncome);
    let hraExempt = 0;
    if (hraReceived > 0 && rentPaid > 0) {
        const metroPct = metroCity ? 0.50 : 0.40;
        hraExempt = Math.min(hraReceived, metroPct * basicSalary, Math.max(0, rentPaid - 0.10 * basicSalary));
    }
    const actual80c = Math.min(section80c, 150000);
    const actual80d = Math.min(section80d, 25000);
    const oldTaxable = Math.max(0, annualIncome - oldStdDeduction - hraExempt - actual80c - actual80d);

    function calcOldTax(taxable) {
        if (taxable <= 250000) return 0;
        let tax = 0;
        let t = taxable;
        if (t > 1000000) { tax += (t - 1000000) * 0.30; t = 1000000; }
        if (t > 500000) { tax += (t - 500000) * 0.20; t = 500000; }
        if (t > 250000) { tax += (t - 250000) * 0.05; }
        return tax;
    }

    let oldTax = calcOldTax(oldTaxable);
    if (oldTaxable <= 500000) oldTax = 0;
    const oldTotal = oldTax + oldTax * 0.04;

    // New regime
    const newStdDeduction = Math.min(75000, annualIncome);
    const newTaxable = Math.max(0, annualIncome - newStdDeduction);

    function calcNewTax(taxable) {
        if (taxable <= 300000) return 0;
        let tax = 0;
        const slabs = [
            [300000, 700000, 0.05],
            [700000, 1000000, 0.10],
            [1000000, 1200000, 0.15],
            [1200000, 1500000, 0.20],
            [1500000, Infinity, 0.30],
        ];
        for (const [lower, upper, rate] of slabs) {
            if (taxable > lower) {
                tax += (Math.min(taxable, upper) - lower) * rate;
            }
        }
        return tax;
    }

    let newTax = calcNewTax(newTaxable);
    if (newTaxable <= 700000) newTax = 0;
    const newTotal = newTax + newTax * 0.04;

    return {
        labels: ["Old Regime", "New Regime"],
        datasets: [
            { label: "Total Tax + Cess", data: [Math.round(oldTotal), Math.round(newTotal)] },
        ],
    };
}
