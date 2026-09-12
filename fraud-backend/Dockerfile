# Use official Eclipse Temurin JDK 17 as base image
FROM eclipse-temurin:17-jdk-jammy AS build

WORKDIR /app

# Copy the Maven wrapper and project object model
COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .

# Grant execution rights to maven wrapper
RUN chmod +x ./mvnw

# Go offline to cache dependencies
RUN ./mvnw dependency:go-offline -B

# Copy the source code
COPY src src

# Package the application
RUN ./mvnw package -DskipTests

# Stage 2: Create a minimal image for production
FROM eclipse-temurin:17-jre-jammy

WORKDIR /app

# Copy the packaged jar from the build stage
COPY --from=build /app/target/fraud-backend-0.0.1-SNAPSHOT.jar app.jar

# Expose port 8080
EXPOSE 8080

# Run the jar file with cloud container optimizations
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
