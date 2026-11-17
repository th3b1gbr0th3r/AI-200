-- Copia literal de la guía ("Create an IVFFlat index").
CREATE INDEX idx_products_embedding_ivfflat
ON products USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

EXPLAIN ANALYZE
SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
FROM products
ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
LIMIT 10;

SET ivfflat.probes = 1;
EXPLAIN ANALYZE
SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
FROM products
ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
LIMIT 10;

SET ivfflat.probes = 50;
EXPLAIN ANALYZE
SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
FROM products
ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
LIMIT 10;
