-- Copia literal de la guía ("Create an HNSW index").
DROP INDEX idx_products_embedding_ivfflat;

SET maintenance_work_mem = '256MB';

CREATE INDEX idx_products_embedding_hnsw
ON products USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

EXPLAIN ANALYZE
SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
FROM products
ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
LIMIT 10;

SET hnsw.ef_search = 20;
EXPLAIN ANALYZE
SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
FROM products
ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
LIMIT 10;

SET hnsw.ef_search = 100;
EXPLAIN ANALYZE
SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
FROM products
ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
LIMIT 10;
