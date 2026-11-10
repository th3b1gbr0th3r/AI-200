-- Task de esquema (guía) · pgvector + tabla products + índice HNSW. Copia literal de la guía.
-- Ejecutar conectado a la BD postgres:  \i sql/schema.sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    description TEXT,
    price NUMERIC(10, 2),
    embedding vector(330)
);

CREATE INDEX products_embedding_idx
ON products USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

\d products
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
