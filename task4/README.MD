# Parser API  
Парсер товаров с сайта divoroom.store с сохранением результатов в базу данных PostgreSQL
 
## Структура проекта

```
task4/
├── main.py              # FastAPI приложение
├── database.py          # Подключение к БД
├── parser.py            # Логика парсинга 
├── docker-compose.yml   # Docker-конфигурация 
├── requirements.txt     
└── README.md            
```

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Работа

```bash
docker-compose up -d postgres
```

### Остановка БД
```bash
# Остановить контейнер
docker-compose down

# Остановить и удалить данные (полный сброс)
docker-compose down -v
```

## Запуск сервера
```
# Активируйте виртуальное окружение
source .venv/bin/activate

# Запустите API сервер
uvicorn main:app --host 127.0.0.1 --port 8000
```

Сервер будет доступен по адресу: http://127.0.0.1:8000

## Использование
### Parse
```bash
# Страница каталого
curl -X POST "http://127.0.0.1:8000/parse?url=https://divoroom.store/catalog"

# Страница отдельного товара
curl -X POST "http://127.0.0.1:8000/parse?url=http://divoroom.store/catalog/tproduct/661904054722-brelki-korovki-vse-rastsvetki"
```

### Чтение из бд
```bash
curl "http://127.0.0.1:8000/products"
```

### Swagger 😎
```
http://localhost:8000/docs
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


