from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import uvicorn
import logging
import os

from database import DatabaseManager
from models import MountainPassData, UserData, PhotoData

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mountain Passes API",
    description="API для учета горных перевалов Федерации Спортивного Туризма России",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене следует указать конкретные домены
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()


@app.post("/submitData",
          response_model=Dict[str, Any],
          status_code=status.HTTP_200_OK,
          summary="Добавление нового перевала",
          description="Добавляет информацию о новом горном перевале в базу данных")
async def submit_data(pass_data: MountainPassData):
    """
    Добавление информации о новом перевале
    """
    try:
        logger.info(f"Получен запрос на добавление перевала: {pass_data.title}")

        # Преобразуем данные в словарь для обработки
        data_dict = pass_data.model_dump()

        # Вызываем метод менеджера БД
        result = db_manager.add_mountain_pass(data_dict)

        # Логируем результат
        if result['status'] == 200:
            logger.info(f"Успешно добавлен перевал с ID: {result['id']}")
        else:
            logger.warning(f"Ошибка при добавлении перевала: {result['message']}")

        # Возвращаем соответствующий HTTP статус
        if result['status'] == 200:
            return result
        elif result['status'] == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['message']
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result['message']
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка в submit_data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@app.get("/submitData/{pass_id}",
         response_model=Dict[str, Any],
         summary="Получение информации о перевале",
         description="Возвращает полную информацию о перевале по его ID")
async def get_pass_data(pass_id: int):
    """
    Получение информации о перевале по ID
    """
    try:
        logger.info(f"Запрос информации о перевале с ID: {pass_id}")

        # Получаем данные из БД
        pass_data = db_manager.get_mountain_pass(pass_id)

        if pass_data is None:
            logger.warning(f"Перевал с ID {pass_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Перевал не найден"
            )

        logger.info(f"Успешно возвращены данные перевала ID: {pass_id}")
        return pass_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении перевала {pass_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении данных: {str(e)}"
        )


@app.patch("/submitData/{pass_id}",
           response_model=Dict[str, Any],
           summary="Редактирование перевала",
           description="Обновляет информацию о существующем перевале. Редактирование возможно только для записей со статусом 'new'")
async def update_pass_data(pass_id: int, pass_data: MountainPassData):
    """
    Редактирование информации о перевале
    """
    try:
        logger.info(f"Запрос на обновление перевала с ID: {pass_id}")

        # Преобразуем данные в словарь
        data_dict = pass_data.model_dump()

        # Вызываем метод обновления
        result = db_manager.update_mountain_pass(pass_id, data_dict)

        # Логируем результат
        if result['state'] == 1:
            logger.info(f"Успешно обновлен перевал ID: {pass_id}")
            return result
        else:
            logger.warning(f"Ошибка при обновлении перевала ID {pass_id}: {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['message']
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обновлении перевала {pass_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@app.get("/submitData/",
         response_model=List[Dict[str, Any]],
         summary="Получение перевалов пользователя",
         description="Возвращает список всех перевалов, добавленных пользователем с указанным email")
async def get_passes_by_user_email(
        user_email: str = Query(
            ...,
            alias="user__email",
            description="Email пользователя для поиска его перевалов",
            examples=["user@example.com"]
        )
):
    """
    Получение всех перевалов, добавленных пользователем
    """
    try:
        logger.info(f"Запрос перевалов пользователя: {user_email}")

        # Получаем данные из БД
        passes = db_manager.get_passes_by_user_email(user_email)

        logger.info(f"Найдено {len(passes)} перевалов для пользователя {user_email}")
        return passes

    except Exception as e:
        logger.error(f"Ошибка при получении перевалов пользователя {user_email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении данных: {str(e)}"
        )


@app.get("/",
         summary="Корневой endpoint",
         description="Возвращает основную информацию о API")
async def root():
    """
    Корневой endpoint API
    """
    return {
        "message": "Mountain Passes API - Система учета горных перевалов",
        "version": "1.0.0",
        "description": "API для Федерация Спортивного Туризма России",
        "docs": "/docs",
        "endpoints": {
            "submit_data": "POST /submitData",
            "get_pass": "GET /submitData/{id}",
            "update_pass": "PATCH /submitData/{id}",
            "get_user_passes": "GET /submitData/?user__email={email}"
        }
    }


@app.get("/health",
         summary="Health check",
         description="Проверка работоспособности сервиса")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Проверяем соединение с БД
        conn = db_manager.get_connection()
        conn.close()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Ошибка соединения с БД: {str(e)}")
        db_status = "unhealthy"

    return {
        "status": "healthy",
        "database": db_status
    }


@app.get("/info",
         summary="Информация о сервисе",
         description="Подробная информация о конфигурации и состоянии сервиса")
async def service_info():
    """
    Информация о сервисе
    """
    return {
        "service": "Mountain Passes API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": {
            "host": os.getenv("FSTR_DB_HOST", "not set"),
            "port": os.getenv("FSTR_DB_PORT", "not set"),
            "database": os.getenv("FSTR_DB_NAME", "not set")
        },
        "features": {
            "cors": True,
            "validation": True,
            "logging": True,
            "health_check": True
        }
    }


# Обработчики ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Обработчик HTTP исключений"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status": exc.status_code
        }
    )




@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    """Обработчик ошибок валидации"""
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Ошибка валидации данных",
            "errors": str(exc),
            "status": 422
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    """Обработчик внутренних ошибок сервера"""
    logger.error(f"Internal Server Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Внутренняя ошибка сервера",
            "status": 500
        }
    )


if __name__ == "__main__":
    # Конфигурация для запуска в различных средах
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT") == "development"

    logger.info(f"Запуск сервера на {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True
    )