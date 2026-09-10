package com.example.fraudbackend;

import ai.onnxruntime.OnnxTensor;
import ai.onnxruntime.OrtEnvironment;
import ai.onnxruntime.OrtException;
import ai.onnxruntime.OrtSession;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.InputStream;
import java.util.Collections;
import java.util.Map;

@Service
public class FraudDetectionService {

    private OrtEnvironment env;
    private OrtSession session;

    @PostConstruct
    public void init() throws Exception {
        env = OrtEnvironment.getEnvironment();
        
        // Load the ONNX model from resources
        ClassPathResource resource = new ClassPathResource("XGBoost.onnx");
        try (InputStream is = resource.getInputStream()) {
            byte[] modelBytes = is.readAllBytes();
            OrtSession.SessionOptions options = new OrtSession.SessionOptions();
            session = env.createSession(modelBytes, options);
        }
    }

    public double predictProbability(float[] features) throws OrtException {
        // ONNX expects a 2D array [batch_size, num_features]
        float[][] inputData = new float[][]{features};
        
        try (OnnxTensor tensor = OnnxTensor.createTensor(env, inputData)) {
            // The input name in the ONNX model converted from xgboost is typically "float_input"
            Map<String, OnnxTensor> inputs = Collections.singletonMap("float_input", tensor);
            
            try (OrtSession.Result result = session.run(inputs)) {
                // The XGBoost ONNX model converted via onnxmltools outputs a 2D float array [batch_size, num_classes] for probabilities.
                float[][] probArray = (float[][]) result.get(1).getValue();
                
                // We want the probability of class 1 (Fraud) for the first instance in the batch
                return probArray[0][1];
            }
        }
    }

    @PreDestroy
    public void close() {
        try {
            if (session != null) session.close();
            if (env != null) env.close();
        } catch (OrtException e) {
            e.printStackTrace();
        }
    }
}
