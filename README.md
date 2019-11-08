Grader NG

```
docker run --rm -d -p 6379:6379 --name test-redis redis
```

```
docker run --rm -d -p 27017:27017 --name=test-mongo mongo
```

```
celery -A graderng worker --loglevel=info
```

## Requirements

Use `sqlparse==0.2.4`
