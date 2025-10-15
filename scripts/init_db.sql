-- Создание базы данных для учета горных перевалов

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица перевалов
CREATE TABLE IF NOT EXISTS mountain_passes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    height INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'pending', 'accepted', 'rejected')),
    add_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица фотографий
CREATE TABLE IF NOT EXISTS photos (
    id SERIAL PRIMARY KEY,
    pass_id INTEGER REFERENCES mountain_passes(id) ON DELETE CASCADE,
    photo_data TEXT,
    photo_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для улучшения производительности
CREATE INDEX IF NOT EXISTS idx_mountain_passes_user_id ON mountain_passes(user_id);
CREATE INDEX IF NOT EXISTS idx_mountain_passes_status ON mountain_passes(status);
CREATE INDEX IF NOT EXISTS idx_photos_pass_id ON photos(pass_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Комментарии к таблицам
COMMENT ON TABLE users IS 'Таблица пользователей, добавляющих перевалы';
COMMENT ON TABLE mountain_passes IS 'Основная таблица с информацией о перевалах';
COMMENT ON TABLE photos IS 'Таблица фотографий перевалов';
COMMENT ON COLUMN mountain_passes.status IS 'Статус модерации: new, pending, accepted, rejected';