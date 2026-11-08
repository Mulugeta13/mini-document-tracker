# Mini Document Tracker

A REST API for managing documents, built with Python, FastAPI, PostgreSQL, and Docker.

## Features

- Create, read, update, and delete documents (CRUD)
- Search documents by title
- Filter documents by sentiment
- Pagination using limit and offset
- Sort documents by ID
- Input validation using Pydantic
- Database connection error handling

## Technologies

- Python
- FastAPI
- PostgreSQL
- Docker
- Psycopg
- Pydantic

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/documents` | Create a document |
| GET | `/documents` | List, search, filter, and sort documents |
| GET | `/documents/{document_id}` | Get a document by ID |
| PUT | `/documents/{document_id}` | Update a document |
| DELETE | `/documents/{document_id}` | Delete a document |

## Getting Started

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies from `requirements.txt`.
4. Start a PostgreSQL database and create the required `documents` table.
5. Create a `.env` file with the database connection settings.
6. Run the FastAPI application:

```bash
python -m uvicorn main:app --reload
```

Open the API documentation at:

`http://127.0.0.1:8000/docs`

## Project Status

Backend API implemented. Frontend development is planned.
