-- Copia literal de la guía ("Analyze baseline performance"). Sin índice: esperado Seq Scan.
EXPLAIN ANALYZE
SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
FROM products
ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
LIMIT 10;
