package com.example.fraudbackend;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import java.time.Instant;

@Document(collection = "inference_logs")
public class InferenceLog {
    
    @Id
    private String id;
    private Instant timestamp;
    private FraudPredictionRequest request;
    private FraudPredictionResponse response;

    public InferenceLog() {}

    public InferenceLog(FraudPredictionRequest request, FraudPredictionResponse response) {
        this.timestamp = Instant.now();
        this.request = request;
        this.response = response;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public Instant getTimestamp() { return timestamp; }
    public void setTimestamp(Instant timestamp) { this.timestamp = timestamp; }

    public FraudPredictionRequest getRequest() { return request; }
    public void setRequest(FraudPredictionRequest request) { this.request = request; }

    public FraudPredictionResponse getResponse() { return response; }
    public void setResponse(FraudPredictionResponse response) { this.response = response; }
}
