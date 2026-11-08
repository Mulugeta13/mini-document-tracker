import os
from dotenv import load_dotenv

load_dotenv()
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal
import psycopg

app = FastAPI()


def get_connection():
    try:
        connection = psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            row_factory=dict_row
        )

        return connection

    except psycopg.OperationalError:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable"
        )

class Document(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=1)
    source: str | None = None
    published_at: datetime | None = None
    sentiment: Literal["positive", "negative", "neutral"] | None = None


class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str


class DocumentDetails(BaseModel):
    id: int
    title: str
    content: str | None = None
    source: str | None = None
    published_at: datetime | None = None
    sentiment: str | None = None
    created_at: datetime


class DocumentDetailsResponse(BaseModel):
    document: DocumentDetails


class DocumentsListResponse(BaseModel):
    documents: list[DocumentDetails]


@app.post(
    "/documents",
    status_code=201,
    response_model=DocumentResponse
)
def create_document(document: Document):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO documents (title, content, source, published_at, sentiment)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            document.title,
            document.content,
            document.source,
            document.published_at,
            document.sentiment
        )
    )

    new_id = cursor.fetchone()["id"]

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "id": new_id,
        "title": document.title,
        "content": document.content
    }


@app.get(
    "/documents",
    response_model=DocumentsListResponse
)
def get_documents(
    sentiment: str | None = None,
    search: str | None = None,
    limit: int = Query(default=5, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort: str = "asc"
):

    connection = get_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM documents WHERE 1=1"
    params = []

    if search is not None:
        query += " AND title ILIKE %s"
        params.append("%" + search + "%")

    if sentiment is not None:
        query += " AND sentiment = %s"
        params.append(sentiment)

    if sort == "desc":
        query += " ORDER BY id DESC"
    else:
        query += " ORDER BY id ASC"

    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(query, params)

    documents = cursor.fetchall()

    cursor.close()
    connection.close()

    return {"documents": documents}


@app.get(
    "/documents/{document_id}",
    response_model=DocumentDetailsResponse
)
def get_document(document_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM documents WHERE id = %s",
        (document_id,)
    )

    document = cursor.fetchone()

    cursor.close()
    connection.close()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {"document": document}


@app.put("/documents/{document_id}")
def update_document(document_id: int, document: Document):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE documents
        SET title = %s,
            content = %s,
            source = %s,
            published_at = %s,
            sentiment = %s
        WHERE id = %s
        """,
        (
            document.title,
            document.content,
            document.source,
            document.published_at,
            document.sentiment,
            document_id
        )
    )

    updated_rows = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    if updated_rows == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {"message": "Document updated successfully"}


@app.delete("/documents/{document_id}")
def delete_document(document_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM documents WHERE id = %s",
        (document_id,)
    )

    deleted_rows = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    if deleted_rows == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {"message": "Document deleted successfully"}


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/hello")
def say_hello():
    return {"message": "Hello FastAPI"}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}


@app.get("/products")
def get_products(Category: str = "all"):
    return {"category": Category}


class User(BaseModel):
    name: str
    age: int


@app.post("/users")
def create_user(user: User):
    return {"name": user.name, "age": user.age}
