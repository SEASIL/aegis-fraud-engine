package com.example.fraudbackend;

import ai.onnxruntime.OrtException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StreamUtils;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;

@RestController
@CrossOrigin(origins = "*")
public class FraudDetectionController {

    @Autowired
    private FraudDetectionService fraudDetectionService;

    @Autowired
    private InferenceLogRepository inferenceLogRepository;

    @PostMapping("/predict")
    public ResponseEntity<Object> predict(@RequestBody FraudPredictionRequest request) {
        try {
            float[] features = request.toFloatArray();
            double prob = fraudDetectionService.predictProbability(features);
            
            // Threshold for fraud could be 0.5, or customized based on PR-AUC
            boolean isFraud = prob >= 0.5;
            
            FraudPredictionResponse response = new FraudPredictionResponse(prob, isFraud);
            
            // Log to MongoDB asynchronously (or synchronously for this project)
            try {
                inferenceLogRepository.save(new InferenceLog(request, response));
            } catch (Exception e) {
                System.err.println("Warning: Failed to log inference to MongoDB: " + e.getMessage());
                // Continue to return prediction even if DB logging fails
            }
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.internalServerError().body("ERROR: " + e.toString());
        }
    }

    @GetMapping("/metrics")
    public ResponseEntity<String> getMetrics() throws IOException {
        ClassPathResource resource = new ClassPathResource("metrics.json");
        String metricsStr = StreamUtils.copyToString(resource.getInputStream(), StandardCharsets.UTF_8);
        return ResponseEntity.ok().header("Content-Type", "application/json").body(metricsStr);
    }

    @GetMapping("/api/logs")
    public ResponseEntity<List<InferenceLog>> getRecentLogs() {
        try {
            return ResponseEntity.ok(inferenceLogRepository.findTop20ByOrderByTimestampDesc());
        } catch (Exception e) {
            System.err.println("Warning: Failed to fetch logs from MongoDB: " + e.getMessage());
            return ResponseEntity.internalServerError().build();
        }
    }
}
