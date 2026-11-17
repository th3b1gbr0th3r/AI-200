-- Copia literal de la guía oficial (sección "Create the database schema and test data").
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    in_stock BOOLEAN DEFAULT true,
    embedding vector(384)
);

INSERT INTO products (name, category_id, price, in_stock, embedding)
SELECT
    'Product ' || i,
    (random() * 20)::int + 1,
    (random() * 1000)::numeric(10,2),
    random() > 0.1,
    ('[' || array_to_string(ARRAY(
        SELECT (random() * 2 - 1)::float4
        FROM generate_series(1, 384)
    ), ',') || ']')::vector
FROM generate_series(1, 100000) AS i;

SELECT COUNT(*) FROM products;

-- Tabla temporal: vive solo en esta sesión de psql.
CREATE TEMP TABLE query_vectors AS
SELECT ('[' || array_to_string(ARRAY(
    SELECT (random() * 2 - 1)::float4
    FROM generate_series(1, 384)
), ',') || ']')::vector AS embedding;
