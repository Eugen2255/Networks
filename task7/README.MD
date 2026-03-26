# Parser API  
Парсер товаров с сайта divoroom.store с сохранением результатов в базу данных PostgreSQL.  
Приложение и база данных находятся в разных докер контейнерах.
 
## Структура проекта

```
task5/
├── main.py              # FastAPI приложение
├── database.py          # Подключение к БД
├── parser.py            # Логика парсинга 
├── Dockerfile           # Образ приложения
├── requirements.txt     
└── README.md            
```
## Архитектура
```
┌───────────────────────────────────────────────────────────────┐
│                      Docker Network                           │
│                                                               │
│                                                               │
│   ┌────────────┐      ┌────────────┐      ┌────────────┐      │
│   │   nginx    │ ──── │    app     │ ──── │     db     │      │
│   │   :80      │      │   :8080    │      │   :5432    │      │
│   └──────┬─────┘      └────────────┘      └────────────┘      │
│          │                                                    │
└──────────┼────────────────────────────────────────────────────┘
       127.0.0.1                                               
     (браузер/curl)                                            
```
## Быстрые команды
```bash
# Ru
curl -H "X-Forwarded-For: 95.24.0.1" http://127.0.0.1/

# ne Ru
curl -H "X-Forwarded-For: 8.8.8.8" http://127.0.0.1/

## Развёртывание 

```bash
# 1 Создать сеть
docker network create task5-network

# 2 Запустить базу данных
docker run -d --name task6-db --network task6-network \
  -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=task6_db -v pg/var/lib/postgresql/data \
  -p 5432:5432 postgres:15-alpine

# 3 Собрать образ приложения
docker build -t task6-app .

# 4 Запустить приложение
docker run -d \
  --name task6-app \
  --network task6-network \
  -p 8080:8080 \
  -e DATABASE_URL="postgresql://user:password@task6-db:5432/task6_db" \
  task6-app

# 5. Запустить nginx
docker run -d --name task6-nginx --network task6-network \
  -p 80:80 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine

# 6. Проверить работу
docker ps
curl http://127.0.0.1/
```


### Остановка и удаление
```bash
docker stop task6-app task6-db task6-nginx
docker rm -f task6-app task6-db task6-nginx
```

## Использование
### Parse
```bash
curl http://127.0.0.1/

curl -X POST "http://127.0.0.1/parse?url=https://divoroom.store/catalog"
```

### Чтение из бд
```bash
curl "http://127.0.0.1/products?limit=50"
```

### Swagger 😎
```
http://127.0.0.1/docs
```


### Пример одного товара в бд

```json
{
    "id": 73,
    "product_id": "366492613102",
    "title": "Брелки Коровки (ВСЕ расцветки)",
    "description": "Брелок 3-4см, фурнитура перламутровые карабины*у брелков с двух сторон защитная прозрачная пленка, ее нужно будет снять",
    "price": "400",
    "url": "http://divoroom.store/catalog/tproduct/661904054722-brelki-korovki-vse-rastsvetki",
    "image": "https://static.tildacdn.com/stor6631-3866-4634-b438-623338333936/79007102.jpg",
    "source_url": "https://divoroom.store/catalog/tproduct/661904054722-brelki-korovki-vse-rastsvetki",
    "parsed_at": "2026-03-11T18:35:07.422779"
}
```