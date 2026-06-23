# ETL Validation Review

## Scope

Reviewed the DataCo source profile, ETL schema, and load path for analytics readiness.

Source profile reference: [scripts/dataco_stats.txt](../scripts/dataco_stats.txt)

## Source Data Summary

- Total source rows: 180,519
- Column count: 53
- Expected target counts by business entity:
  - categories: 51
  - departments: 11
  - customers: 20,652
  - products: 118
  - orders: 65,752
  - order_items: 180,519
  - shipments: 65,752

## Validation Findings

### Critical Blockers

1. Customer email loading will fail against the current schema.
   - The raw source masks every email value as XXXXXXXXX.
   - The ETL cleaner converts masked PII to null.
   - customers.email is defined as non-nullable in the ORM model.
   - Result: customer inserts will violate a NOT NULL constraint unless the schema or load strategy changes.

2. Category uniqueness is inconsistent with the source.
   - Source profile shows 51 category IDs but only 50 category names.
   - categories.name is unique in the model.
   - Result: a duplicate category name or non-1:1 mapping can trigger unique constraint failures during load.

### Data Quality Issues

- Product Description is 100% empty in the source. This is acceptable only if analytics do not require product descriptions.
- Order Zipcode is null for 86.24% of rows, so postal-code-based analytics will be weak.
- Customer Email and Customer Password are fully masked in the source, which means they are not usable as real customer attributes.
- Late_delivery_risk is cleanly binary and suitable for downstream metrics.
- Numeric and date fields appear structurally consistent in the sampled profile.

### Loading and Schema Issues

- customers.email should be nullable or replaced with a surrogate/business-safe value if the source cannot provide real emails.
- categories.name should not be globally unique unless the source is guaranteed to be unique by name.
- shipments.id = order_id assumes one shipment per order. That is acceptable only if the business rule is strictly one-to-one.
- order_items.id is used as the primary key, which is fine if the dataset guarantees uniqueness, and the source profile suggests it does.

## SQL Verification Checklist

Run these in Postgres after the load.

### Row Counts

- SELECT COUNT(*) FROM categories;
- SELECT COUNT(*) FROM departments;
- SELECT COUNT(*) FROM customers;
- SELECT COUNT(*) FROM products;
- SELECT COUNT(*) FROM orders;
- SELECT COUNT(*) FROM order_items;
- SELECT COUNT(*) FROM shipments;

### Foreign Key Integrity

- products.category_id must match categories.id
- products.department_id must match departments.id
- orders.customer_id must match customers.id
- order_items.order_id must match orders.id
- order_items.product_id must match products.id
- shipments.order_id must match orders.id

### Duplicate Checks

- categories.id, categories.external_category_id, categories.name
- departments.id, departments.external_department_id, departments.name
- customers.id, customers.email
- products.id
- orders.id
- order_items.id
- shipments.id

### Null Distribution Checks

- customers.email
- customers.password_hash
- products.description
- products.image_url
- orders.zipcode
- shipments.delivery_status
- shipments.late_delivery_risk

### Invalid Record Checks

- order_items.quantity > 0
- order_items.unit_price >= 0
- order_items.line_total >= 0
- order_items.discount_rate between 0 and 1
- order_items.profit_ratio between 0 and 1

## Data Quality Report Template

### 1. Load Summary

- Source file:
- Load date:
- Job ID:
- Total staged rows:
- Total valid rows:
- Total rejected rows:
- Total loaded rows:

### 2. Table-Level Results

- categories: row count, duplicates, nulls, FK issues
- departments: row count, duplicates, nulls, FK issues
- customers: row count, duplicates, nulls, FK issues
- products: row count, duplicates, nulls, FK issues
- orders: row count, duplicates, nulls, FK issues
- order_items: row count, duplicates, nulls, FK issues
- shipments: row count, duplicates, nulls, FK issues

### 3. Issue Log

- Issue ID:
- Severity:
- Table:
- Column:
- Description:
- Impact:
- Recommended fix:
- Owner:
- Status:

### 4. Analytics Readiness Decision

- Ready / Not ready
- Blocking issues:
- Required remediation before analytics:

## Readiness Assessment

Current status: not ready for analytics.

Reason: the source profile and schema together expose at least two blocking issues for a production load, namely masked customer email values loading into a non-nullable column and category name uniqueness not matching source cardinality.

Recommended next action: fix the customer identity strategy and category uniqueness rule, then run the SQL verification checklist against the live database.