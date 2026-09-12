package com.example.fraudbackend;

import org.springframework.data.mongodb.repository.MongoRepository;
import java.util.List;

public interface InferenceLogRepository extends MongoRepository<InferenceLog, String> {
    List<InferenceLog> findTop20ByOrderByTimestampDesc();
}
