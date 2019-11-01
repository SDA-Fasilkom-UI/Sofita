Grader NG

```
docker run --rm -d -p 5672:5672 --name=test-rabbitmq rabbitmq
```

```
docker run --rm -d -p 27017:27017 --name=test-mongo mongo
```

## Requirements
* Jangan menggunakan sqlparse terbaru, tetapi gunakan versi 0.2.4