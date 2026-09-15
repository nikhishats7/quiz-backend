# quiz-backend

## To run:

```jsx
.\mvnw.cmd spring-boot:run
```

## Redis commands

```jsx
#To start the container
docker run --name quiz-redis -p 6379:6379 -d redis:7-alpine

#To monitor
docker exec -it quiz-redis redis-cli MONITOR

#To view existing caches and its key
docker exec -it quiz-redis redis-cli --scan --pattern "*"

#To view remaining TTL in seconds
docker exec quiz-redis redis-cli TTL "allQuestions::SimpleKey []"
```