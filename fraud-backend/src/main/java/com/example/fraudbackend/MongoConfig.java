package com.example.fraudbackend;

import com.mongodb.ConnectionString;
import com.mongodb.MongoClientSettings;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.repository.config.EnableMongoRepositories;

@Configuration
@EnableMongoRepositories(basePackages = "com.example.fraudbackend")
public class MongoConfig {

    // Connection string is hardcoded here to bypass all Spring Boot
    // property/environment variable parsing issues on Render.
    private static final String MONGO_URI =
        "mongodb+srv://asifsekh117_db_user:EnJkqnV44jxs77bT" +
        "@frauddetec0.f4rh6ry.mongodb.net/fraud_inference" +
        "?appName=frauddetec0";

    @Bean
    public MongoClient mongoClient() {
        ConnectionString cs = new ConnectionString(MONGO_URI);
        MongoClientSettings settings = MongoClientSettings.builder()
                .applyConnectionString(cs)
                .build();
        return MongoClients.create(settings);
    }

    @Bean
    public MongoTemplate mongoTemplate(MongoClient mongoClient) {
        return new MongoTemplate(mongoClient, "fraud_inference");
    }
}
