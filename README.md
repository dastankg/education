# Django Events API

REST API проект на Django для управления образовательными событиями с аутентификацией пользователей и поддержкой облачного хранилища медиафайлов.

## 🚀 Возможности

- **Аутентификация пользователей**: JWT + подтверждение по электронной почте (через `django-allauth`)
- **Управление событиями**: 
- **Документация API**: `drf-spectacular` (OpenAPI 3)
- **Хранилище медиа**: S3-совместимое облако
- **Кэширование**: Redis
- **Контейнеризация**: Docker + Docker Compose

## 🛠️ Технологии

- Django 4.x, Django REST Framework
- PostgreSQL
- Redis
- S3-compatible storage
- drf-spectacular
- JWT, Email verification (django-allauth)
- Docker / Docker Compose

## 📋 Требования

- Docker и Docker Compose
- Учетная запись S3-хранилища (например, TimeWeb)
- SMTP-сервер для верификации email

## 🔧 Установка и запуск

### 1. Клонирование репозитория

```bash
    git clone https://github.com/your-name/events-api.git
    cd events-api
```
### 2. Настройка переменных окружения
Создайте .env файл и заполните на основе example:
    
```bash
    cp env_example .env
```
## 3. Запуск с Docker Compose
```bash
    docker-compose up --build -d
```