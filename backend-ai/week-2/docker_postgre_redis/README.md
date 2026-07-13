# Week 2 Implementation

In Week 2, we extended the Week 1 Flask application by replacing the in-memory/CSV-based storage with **PostgreSQL**, adding **Redis** for key-value operations, containerizing the application using **Docker**.

---

# Features Implemented

- **Home Route (`/`)**
  - Returns a welcome message indicating the server is running.

- **Health Check (`/status`)**
  - Returns a JSON response confirming the application is healthy.

- **PostgreSQL CRUD API (`/data`)**
  - Create student records.
  - Retrieve student records.
  - Update student records.
  - Delete student records.

- **Redis CRUD API (`/redis-data`)**
  - Store key-value pairs.
  - Retrieve stored key-value pairs.
  - Update existing values.
  - Delete keys.

- **Swagger UI**
  - API documentation.
  - Interactive endpoint testing.

- **Docker Support**
  - `Dockerfile`
  - `docker-compose.yml`

- **Environment Configuration**
  - `.env`
  - `.env.example`

- **Dependency Management**
  - `requirements.txt`

- **Database Performance Analysis**
  - `EXPLAIN ANALYZE`
  - Indexed vs Non-Indexed query comparison.

---

# API Endpoints

## Home

### GET /

```bash
curl -X GET \
https://symmetrical-adventure-pjgjv7rr6vjgc74j-8000.app.github.dev/
```

---

## Health Check

### GET /status

```bash
curl -X GET \
https://symmetrical-adventure-pjgjv7rr6vjgc74j-8000.app.github.dev/status
```

---

# PostgreSQL CRUD

## GET /data

Retrieve all student records.

```bash
curl -X GET \
https://symmetrical-adventure-pjgjv7rr6vjgc74j-8000.app.github.dev/data
```

---

## POST /data

Create a new student record.

```bash
curl -X POST \
https://symmetrical-adventure-pjgjv7rr6vjgc74j-8000.app.github.dev/data \
-H "Content-Type: application/json" \
-d '{
    "name": "John",
    "age": 21,
    "department": "CSE",
    "academic_year": 3,
    "sgpa": 8.7
}'
```

---

## PUT /data

Update an existing student record.

```bash
curl -X PUT \
https://symmetrical-adventure-pjgjv7rr6vjgc74j-8000.app.github.dev/data \
-H "Content-Type: application/json" \
-d '{
    "id": 1,
    "name": "John Updated",
    "age": 22,
    "department": "CSE",
    "academic_year": 4,
    "sgpa": 9.1
}'
```

---

## DELETE /data

Delete a student record.

```bash
curl -X DELETE \
https://symmetrical-adventure-pjgjv7rr6vjgc74j-8000.app.github.dev/data \
-H "Content-Type: application/json" \
-d '{
    "id": 1
}'
```

---

# Redis CRUD

## GET /redis-data

Retrieve all stored key-value pairs.

```bash
curl -X GET \
https://symmetrical-adventure-pjgjv7rr6vjgc74j-8000.app.github.dev/redis-data
```

---

## POST /redis-data

Create a new key-value pair.

```bash
curl -X POST \
https://symmetrical-adventure-pjgjv7rr6vjgc74j-8000.app.github.dev/redis-data \
-H "Content-Type: application/json" \
-d '{
    "key": "student:1",
    "value": "John Doe"
}'
```

---

## PUT /redis-data

Update an existing key-value pair.

```bash
curl -X PUT \
https://symmetrical-adventure-pjgjv7rr6vjgc74j-8000.app.github.dev/redis-data \
-H "Content-Type: application/json" \
-d '{
    "key": "student:1",
    "value": "John Updated"
}'
```

---

## DELETE /redis-data

Delete a key-value pair.

```bash
curl -X DELETE \
https://symmetrical-adventure-pjgjv7rr6vjgc74j-8000.app.github.dev/redis-data \
-H "Content-Type: application/json" \
-d '{
    "key": "student:1"
}'
```

---

# Running the Application

Build and start the complete application stack:

```bash
docker compose up --build
```

This command starts:

- Flask Application
- PostgreSQL Database
- Redis Server

using the configuration defined in `docker-compose.yml`.