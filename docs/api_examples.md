# Примеры использования API

## Добавление нового перевала

```bash
curl -X POST "http://localhost:8000/submitData" \
-H "Content-Type: application/json" \
-d '{
  "title": "Перевал Дятлова",
  "latitude": 61.750312,
  "longitude": 59.465139,
  "height": 1079,
  "user": {
    "email": "tourist@example.com",
    "full_name": "Петров Иван Сергеевич",
    "phone": "+79123456789"
  },
  "photos": [
    {
      "url": "https://example.com/photo1.jpg"
    },
    {
      "data": "base64_encoded_image_data_here"
    }
  ]
}'
