Grader NG

```
docker run --rm -d -p 5672:5672 --name=test-rabbitmq rabbitmq
```

```
docker run --rm -d -p 27017:27017 --name=test-mongo mongo
```

```
celery -A graderng worker --loglevel=info
```

## Requirements

Use `sqlparse==0.2.4`
