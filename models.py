from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import re

class UserData(BaseModel):
    """Модель данных пользователя"""
    email: str = Field(..., description="Email пользователя")
    full_name: str = Field(..., min_length=2, description="ФИО пользователя")
    phone: str = Field(..., min_length=5, description="Номер телефона")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Некорректный формат email')
        return v

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        return v.strip()

class PhotoData(BaseModel):
    """Модель данных фотографии"""
    data: Optional[str] = None
    url: Optional[str] = None

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('URL должен начинаться с http:// или https://')
        return v

class MountainPassData(BaseModel):
    """Основная модель данных перевала"""
    title: str = Field(..., min_length=2, description="Название перевала")
    latitude: float = Field(..., ge=-90, le=90, description="Широта от -90 до 90")
    longitude: float = Field(..., ge=-180, le=180, description="Долгота от -180 до 180")
    height: int = Field(..., gt=0, le=10000, description="Высота в метрах")
    user: UserData
    photos: List[PhotoData] = Field(default_factory=list, max_length=10)

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        return v.strip()