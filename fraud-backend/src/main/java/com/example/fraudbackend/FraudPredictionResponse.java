package com.example.fraudbackend;

public class FraudPredictionResponse {
    private double fraudProbability;
    private boolean isFraud;

    public FraudPredictionResponse() {}

    public FraudPredictionResponse(double fraudProbability, boolean isFraud) {
        this.fraudProbability = fraudProbability;
        this.isFraud = isFraud;
    }

    public double getFraudProbability() { return fraudProbability; }
    public void setFraudProbability(double fraudProbability) { this.fraudProbability = fraudProbability; }

    public boolean isFraud() { return isFraud; }
    public void setFraud(boolean isFraud) { this.isFraud = isFraud; }
}
