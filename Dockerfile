FROM maven:4.0.0-openjdk-23 AS build
COPY . .
RUN mvn clean package -DskipTests

FROM openjdk:23.0.2-jdk-slim
COPY --from=build /target/quizapp-0.0.1-SNAPSHOT.jar demo.jar
EXPOSE 8080
ENTRYPOINT ["java","-jar","demo.jar"]