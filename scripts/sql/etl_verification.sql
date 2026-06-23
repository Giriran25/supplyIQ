-- ETL Verification and Data Quality Checks

-- Row counts
SELECT 'categories' AS table_name, COUNT(*) AS row_count FROM categories;
SELECT 'departments' AS table_name, COUNT(*) AS row_count FROM departments;
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers;
SELECT 'products' AS table_name, COUNT(*) AS row_count FROM products;
SELECT 'orders' AS table_name, COUNT(*) AS row_count FROM orders;
SELECT 'order_items' AS table_name, COUNT(*) AS row_count FROM order_items;
SELECT 'shipments' AS table_name, COUNT(*) AS row_count FROM shipments;

-- Foreign key integrity
SELECT COUNT(*) AS missing_categories
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
WHERE c.id IS NULL;

SELECT COUNT(*) AS missing_departments
FROM products p
LEFT JOIN departments d ON p.department_id = d.id
WHERE d.id IS NULL;

SELECT COUNT(*) AS missing_customers
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
WHERE c.id IS NULL;

SELECT COUNT(*) AS missing_order_parents
FROM order_items oi
LEFT JOIN orders o ON oi.order_id = o.id
WHERE o.id IS NULL;

SELECT COUNT(*) AS missing_product_parents
FROM order_items oi
LEFT JOIN products p ON oi.product_id = p.id
WHERE p.id IS NULL;

SELECT COUNT(*) AS missing_shipments
FROM shipments s
LEFT JOIN orders o ON s.order_id = o.id
WHERE o.id IS NULL;

-- Duplicate detection examples (run per table as needed)
-- Example: duplicate external_category_id
SELECT external_category_id, COUNT(*) AS dup_count FROM categories GROUP BY external_category_id HAVING COUNT(*) > 1;

-- Null distributions (example)
SELECT
  COUNT(*) FILTER (WHERE email IS NULL) AS missing_email,
  COUNT(*) FILTER (WHERE password_hash IS NULL) AS missing_password_hash,
  COUNT(*) FILTER (WHERE zipcode IS NULL) AS missing_zipcode
FROM customers;

-- Invalid order_items
SELECT * FROM order_items WHERE quantity <= 0 OR unit_price < 0 OR line_total < 0 OR discount_rate < 0 OR discount_rate > 1 OR profit_ratio < 0 OR profit_ratio > 1 LIMIT 100;

-- ETL audit summaries
SELECT COUNT(*) AS staged_rows, SUM(CASE WHEN validated THEN 1 ELSE 0 END) AS validated_rows, SUM(CASE WHEN NOT validated THEN 1 ELSE 0 END) AS invalid_rows FROM staging_dataco;

SELECT stage, error_code, COUNT(*) AS failures FROM etl_errors GROUP BY stage, error_code ORDER BY COUNT(*) DESC;
