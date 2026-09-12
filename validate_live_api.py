"""
Aegis Fraud Engine - Live API Validation Script
================================================
Sends known FRAUD and LEGITIMATE transactions to the live API
and checks if the model correctly identifies them.

These test cases are hand-crafted based on the statistical
distributions found in the IEEE-CIS Fraud Detection dataset.
"""
import urllib.request
import json

API_URL = "https://aegis-fraud-backend.onrender.com/predict"

# -----------------------------------------------------------------------
# Test Cases: Each has the 7 features the model expects + ground truth
# -----------------------------------------------------------------------
# Features: transactionAmt, card1, pEmaildomainFreq, card4Freq,
#           productCdFreq, amtZScoreCard1, cardTxCount24h
# -----------------------------------------------------------------------

test_cases = [
    {
        "label": "LEGITIMATE - Normal Coffee Purchase",
        "expected": "NOT FRAUD",
        "payload": {
            "transactionAmt": 15.5,
            "card1": 10486.0,
            "pEmaildomainFreq": 0.12,
            "card4Freq": 0.65,
            "productCdFreq": 0.75,
            "amtZScoreCard1": 0.1,
            "cardTxCount24h": 2.0
        }
    },
    {
        "label": "LEGITIMATE - Regular Online Purchase",
        "expected": "NOT FRAUD",
        "payload": {
            "transactionAmt": 49.99,
            "card1": 9876.0,
            "pEmaildomainFreq": 0.25,
            "card4Freq": 0.70,
            "productCdFreq": 0.80,
            "amtZScoreCard1": 0.3,
            "cardTxCount24h": 3.0
        }
    },
    {
        "label": "FRAUD - Card Testing Attack (many small txns)",
        "expected": "FRAUD",
        "payload": {
            "transactionAmt": 1.0,
            "card1": 5555.0,
            "pEmaildomainFreq": 0.001,
            "card4Freq": 0.10,
            "productCdFreq": 0.05,
            "amtZScoreCard1": -2.5,
            "cardTxCount24h": 47.0
        }
    },
    {
        "label": "FRAUD - Velocity Spike (huge unusual amount)",
        "expected": "FRAUD",
        "payload": {
            "transactionAmt": 4500.0,
            "card1": 1234.0,
            "pEmaildomainFreq": 0.002,
            "card4Freq": 0.08,
            "productCdFreq": 0.03,
            "amtZScoreCard1": 8.7,
            "cardTxCount24h": 31.0
        }
    },
    {
        "label": "FRAUD - Rare domain + unusual pattern",
        "expected": "FRAUD",
        "payload": {
            "transactionAmt": 299.0,
            "card1": 7777.0,
            "pEmaildomainFreq": 0.0005,
            "card4Freq": 0.04,
            "productCdFreq": 0.02,
            "amtZScoreCard1": 5.2,
            "cardTxCount24h": 22.0
        }
    },
]

# -----------------------------------------------------------------------
# Run the tests
# -----------------------------------------------------------------------
def call_api(payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("=" * 65)
print("   AEGIS FRAUD ENGINE - LIVE API VALIDATION")
print("=" * 65)
print(f"   Endpoint: {API_URL}\n")

passed = 0
failed = 0

for i, tc in enumerate(test_cases, 1):
    print(f"[Test {i}] {tc['label']}")
    try:
        result = call_api(tc["payload"])
        prob = result.get("fraudProbability", 0)
        is_fraud = result.get("isFraud", False)
        predicted = "FRAUD" if is_fraud else "NOT FRAUD"
        expected = tc["expected"]
        status = "✅ PASS" if predicted == expected else "❌ FAIL"

        if predicted == expected:
            passed += 1
        else:
            failed += 1

        print(f"   Fraud Probability : {prob * 100:.1f}%")
        print(f"   Predicted         : {predicted}")
        print(f"   Expected          : {expected}")
        print(f"   Result            : {status}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        failed += 1
    print()

print("=" * 65)
print(f"   RESULTS: {passed} passed / {passed + failed} total")
if failed == 0:
    print("   🎉 ALL TESTS PASSED! Your model is working correctly.")
else:
    print(f"   ⚠️  {failed} test(s) failed. Review predictions above.")
print("=" * 65)
