const form = document.getElementById('prediction-form');
const riskCircle = document.getElementById('risk-circle');
const riskPercentage = document.getElementById('risk-percentage');
const riskStatus = document.getElementById('risk-status');
const latencyText = document.getElementById('latency-text');
const curlCode = document.getElementById('curl-code');

const presets = {
    normal: {
        transactionAmt: 15.50,
        card1: 10486,
        pEmaildomainFreq: 0.12,
        card4Freq: 0.65,
        productCdFreq: 0.75,
        amtZScoreCard1: 0.1,
        cardTxCount24h: 2
    },
    spike: {
        transactionAmt: 1250.00,
        card1: 9500,
        pEmaildomainFreq: 0.01,
        card4Freq: 0.65,
        productCdFreq: 0.05,
        amtZScoreCard1: 4.8,
        cardTxCount24h: 15
    },
    probe: {
        transactionAmt: 1.00,
        card1: 4444,
        pEmaildomainFreq: 0.05,
        card4Freq: 0.10,
        productCdFreq: 0.75,
        amtZScoreCard1: -1.2,
        cardTxCount24h: 8
    }
};

function loadPreset(type) {
    const data = presets[type];
    for (const key in data) {
        document.getElementById(key).value = data[key];
    }
    updateCurl();
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
    
    // Stroke dasharray calculates the length of the arc
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
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No logs found</td></tr>';
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
            
            return `<tr>
                <td>${time}</td>
                <td>${amt}</td>
                <td>${score}</td>
                <td>${badge}</td>
            </tr>`;
        }).join('');
    } catch (e) {
        console.error("Could not fetch logs", e);
    }
}

form.addEventListener('input', updateCurl);

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
        
        // Refresh logs after a short delay to allow DB insert
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
loadPreset('normal');
fetchLogs();
