package com.example.fraudbackend;

import ai.onnxruntime.*;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.Map;

public class TestONNX {
    public static void main(String[] args) throws Exception {
        OrtEnvironment env = OrtEnvironment.getEnvironment();
        byte[] modelBytes = Files.readAllBytes(Paths.get("src/main/resources/XGBoost.onnx"));
        OrtSession session = env.createSession(modelBytes, new OrtSession.SessionOptions());
        
        for (Map.Entry<String, NodeInfo> entry : session.getInputInfo().entrySet()) {
            System.out.println("Input Name: " + entry.getKey());
            System.out.println("Input Info: " + entry.getValue().getInfo());
        }
        
        for (Map.Entry<String, NodeInfo> entry : session.getOutputInfo().entrySet()) {
            System.out.println("Output Name: " + entry.getKey());
            System.out.println("Output Info: " + entry.getValue().getInfo());
        }

        float[][] inputData = new float[][]{{150.5f, 10486.0f, 0.05f, 0.65f, 0.75f, 1.2f, 5.0f}};
        OnnxTensor tensor = OnnxTensor.createTensor(env, inputData);
        
        String inputName = session.getInputInfo().keySet().iterator().next();
        OrtSession.Result result = session.run(Collections.singletonMap(inputName, tensor));
        
        System.out.println("Result 0: " + result.get(0).getValue());
        System.out.println("Result 0 class: " + result.get(0).getValue().getClass());
        
        if (result.size() > 1) {
            System.out.println("Result 1 class: " + result.get(1).getValue().getClass());
            System.out.println("Result 1: " + result.get(1).getValue());
        }
    }
}
