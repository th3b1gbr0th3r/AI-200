-- Copia literal de la guía ("Implement metadata filtering with indexes").
CREATE INDEX idx_products_category ON products (category_id);

EXPLAIN ANALYZE
SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
FROM products
WHERE category_id = 5
ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
LIMIT 10;

EXPLAIN ANALYZE
SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
FROM products
WHERE category_id = 5 AND price BETWEEN 100 AND 200
ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
LIMIT 10;

CREATE INDEX idx_products_category_price ON products (category_id, price);

EXPLAIN ANALYZE
SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
FROM products
WHERE category_id = 5 AND price BETWEEN 100 AND 200
ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
LIMIT 10;
