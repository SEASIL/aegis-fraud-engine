package com.example.fraudbackend;

import org.springframework.data.mongodb.repository.MongoRepository;

public interface InferenceLogRepository extends MongoRepository<InferenceLog, String> {
}
