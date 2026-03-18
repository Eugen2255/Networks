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

## Развёртывание 

```bash
# 1 Создать сеть
docker network create task5-network

# 2 Запустить базу данных
docker run -d --name task5-db --network task5-network \
  -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=task5_db -v pg/var/lib/postgresql/data \
  -p 5432:5432 postgres:15-alpine

# 3 Собрать образ приложения
docker build -t task5-app .

# 4 Запустить приложение
docker run -d --name task5-app --network task5-network \
  -p 8080:8080 \
  -e DATABASE_URL="postgresql://user:password@task5-db:5432/task5_db" \
  task5-app

# 5 Проверить работу
docker ps
curl http://127.0.0.1:8080/
```


### Остановка и удаление
```bash
docker stop task5-app task5-db
docker rm -f divoroom-app divoroom-db
```

## Использование
### Parse
```bash
# Страница каталого
curl -X POST "http://127.0.0.1:8080/parse?url=https://divoroom.store/catalog"

# Страница отдельного товара
curl -X POST "http://127.0.0.1:8080/parse?url=http://divoroom.store/catalog/tproduct/661904054722-brelki-korovki-vse-rastsvetki"
```

### Чтение из бд
```bash
curl "http://127.0.0.1:8080/products"
```

### Swagger 😎
```
http://localhost:8080/docs
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