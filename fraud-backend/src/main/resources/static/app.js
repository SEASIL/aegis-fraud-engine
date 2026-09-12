const riskCircle = document.getElementById('risk-circle');
const riskPercentage = document.getElementById('risk-percentage');
const riskStatus = document.getElementById('risk-status');
const latencyText = document.getElementById('latency-text');
const curlCode = document.getElementById('curl-code');

const scenarios = {
    coffee: {
        story: "Asif buys a $15.50 coffee using his Visa card at Starbucks. He uses his Gmail account, shops frequently at this chain, and has only 2 transactions today — a perfectly normal Friday morning.",
        data: { transactionAmt: 15.50, card1: 10486, pEmaildomainFreq: 0.25, card4Freq: 0.65, productCdFreq: 0.75, amtZScoreCard1: 0.1, cardTxCount24h: 2 }
    },
    shopping: {
        story: "Sarah orders $120 worth of books on Amazon using her Mastercard. Her Gmail account is common, the card is used regularly, and she has made 3 purchases this week — all expected behaviour.",
        data: { transactionAmt: 120.00, card1: 9876, pEmaildomainFreq: 0.25, card4Freq: 0.70, productCdFreq: 0.80, amtZScoreCard1: 0.4, cardTxCount24h: 3 }
    },
    stolen: {
        story: "A fraudster obtained a stolen card number and is running a 'card testing' attack — making 47 small $1-$5 charges in under one hour to verify the card is active before making a large purchase.",
        data: { transactionAmt: 1.00, card1: 5555, pEmaildomainFreq: 0.001, card4Freq: 0.08, productCdFreq: 0.05, amtZScoreCard1: -2.5, cardTxCount24h: 47 }
    },
    takeover: {
        story: "Someone hacked into a bank account and is attempting a $4,500 wire transfer using a burner email from a rare domain. This is 8.7 standard deviations above this card's normal spend — a massive red flag.",
        data: { transactionAmt: 4500.00, card1: 1234, pEmaildomainFreq: 0.0005, card4Freq: 0.04, productCdFreq: 0.03, amtZScoreCard1: 8.7, cardTxCount24h: 31 }
    },
    international: {
        story: "A $999 purchase from an unusual card network using a rare email domain with 12 transactions today. Not definitively fraud, but the combination of rare signals warrants a manual review.",
        data: { transactionAmt: 999.00, card1: 7777, pEmaildomainFreq: 0.005, card4Freq: 0.06, productCdFreq: 0.04, amtZScoreCard1: 3.2, cardTxCount24h: 12 }
    },
    custom: {
        story: "Enter your own values below to manually test the model with custom ML feature inputs.",
        data: { transactionAmt: 0, card1: 0, pEmaildomainFreq: 0, card4Freq: 0, productCdFreq: 0, amtZScoreCard1: 0, cardTxCount24h: 0 }
    }
};

let currentScenario = 'coffee';

function selectScenario(key) {
    currentScenario = key;

    // Update active button
    document.querySelectorAll('.scenario-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`scenario-${key}`).classList.add('active');

    // Show story
    document.getElementById('scenario-story').textContent = scenarios[key].story;

    // Show/hide technical fields for custom mode
    const isCustom = key === 'custom';
    document.getElementById('technical-fields').style.display = isCustom ? 'grid' : 'none';

    // Fill hidden fields with scenario data
    const data = scenarios[key].data;
    for (const field in data) {
        document.getElementById(field).value = data[field];
    }

    // Update Under the Hood values
    updateHoodValues(data);
    updateCurl();
}

function updateHoodValues(data) {
    const labels = {
        transactionAmt: 'Transaction Amount',
        card1: 'Card 1 ID',
        pEmaildomainFreq: 'Email Domain Freq',
        card4Freq: 'Card 4 Network Freq',
        productCdFreq: 'Product Code Freq',
        amtZScoreCard1: 'Amount Z-Score',
        cardTxCount24h: '24h Tx Count'
    };
    const grid = document.getElementById('hood-values');
    grid.innerHTML = Object.entries(data).map(([k, v]) =>
        `<div class="hood-item"><span class="hood-label">${labels[k]}</span><span class="hood-value">${v}</span></div>`
    ).join('');
}

function updateCurl() {
    const data = getFormData();
    const json = JSON.stringify(data, null, 2);
    const host = window.location.origin;
    curlCode.textContent = `curl -X POST ${host}/predict \\\n  -H "Content-Type: application/json" \\\n  -d '${json}'`;
}

function getFormData() {
    return {
        transactionAmt: parseFloat(document.getElementById('transactionAmt').value) || 0,
        card1: parseFloat(document.getElementById('card1').value) || 0,
        pEmaildomainFreq: parseFloat(document.getElementById('pEmaildomainFreq').value) || 0,
        card4Freq: parseFloat(document.getElementById('card4Freq').value) || 0,
        productCdFreq: parseFloat(document.getElementById('productCdFreq').value) || 0,
        amtZScoreCard1: parseFloat(document.getElementById('amtZScoreCard1').value) || 0,
        cardTxCount24h: parseFloat(document.getElementById('cardTxCount24h').value) || 0
    };
}

function updateGauge(probability) {
    const percent = Math.round(probability * 100);
    riskPercentage.textContent = `${percent}%`;
    const dash = `${percent}, 100`;
    riskCircle.setAttribute('stroke-dasharray', dash);

    if (percent < 30) {
        riskCircle.style.stroke = 'var(--success)';
        riskStatus.textContent = 'LOW RISK (CLEARED)';
        riskStatus.style.color = 'var(--success)';
    } else if (percent < 60) {
        riskCircle.style.stroke = 'var(--warning)';
        riskStatus.textContent = 'MEDIUM (REVIEW)';
        riskStatus.style.color = 'var(--warning)';
    } else {
        riskCircle.style.stroke = 'var(--danger)';
        riskStatus.textContent = 'CRITICAL (BLOCKED)';
        riskStatus.style.color = 'var(--danger)';
    }
}

async function fetchLogs() {
    try {
        const response = await fetch('/api/logs');
        if (!response.ok) return;
        const logs = await response.json();
        const tbody = document.getElementById('logs-body');

        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No logs yet — run a check!</td></tr>';
            return;
        }

        tbody.innerHTML = logs.map(log => {
            const time = new Date(log.timestamp).toLocaleTimeString();
            const amt = `$${log.request.transactionAmt.toFixed(2)}`;
            const score = `${Math.round(log.response.fraudProbability * 100)}%`;
            const isFraud = log.response.fraud;
            const badge = isFraud
                ? '<span class="status-badge status-fraud">FRAUD</span>'
                : '<span class="status-badge status-safe">SAFE</span>';
            return `<tr><td>${time}</td><td>${amt}</td><td>${score}</td><td>${badge}</td></tr>`;
        }).join('');
    } catch (e) {
        console.error("Could not fetch logs", e);
    }
}

const form = document.getElementById('prediction-form');
form.addEventListener('input', () => {
    if (currentScenario === 'custom') {
        updateHoodValues(getFormData());
        updateCurl();
    }
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = getFormData();
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.textContent = 'Scoring...';
    submitBtn.disabled = true;

    try {
        const start = performance.now();
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        const end = performance.now();
        updateGauge(result.fraudProbability);
        latencyText.textContent = `Inference latency: ${(end - start).toFixed(1)}ms`;
        setTimeout(fetchLogs, 500);
    } catch (error) {
        riskStatus.textContent = 'API ERROR';
        riskStatus.style.color = 'var(--danger)';
        console.error(error);
    } finally {
        submitBtn.textContent = 'Run Fraud Check';
        submitBtn.disabled = false;
    }
});

function copyCurl() {
    navigator.clipboard.writeText(curlCode.textContent);
    const btn = document.getElementById('copy-btn');
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = 'Copy', 2000);
}

// Init
selectScenario('coffee');
fetchLogs();
