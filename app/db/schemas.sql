-- PostgreSQL schema for SupplyChainIQ

CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name TEXT NOT NULL,
    region TEXT,
    category TEXT,
    reliability_score NUMERIC(5,2),
    risk_score NUMERIC(5,2),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    product_category TEXT,
    unit_price NUMERIC(12,2),
    cost NUMERIC(12,2),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL,
    customer_region TEXT,
    total_value NUMERIC(12,2),
    status TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE shipments (
    shipment_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id) ON DELETE SET NULL,
    supplier_id INT REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
    product_id INT REFERENCES products(product_id) ON DELETE SET NULL,
    ship_date DATE,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    transit_time_days INT,
    delay_days INT,
    delayed BOOLEAN,
    carrier TEXT,
    region TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(product_id),
    warehouse_id INT,
    region TEXT,
    stock_level INT,
    safety_stock INT,
    reorder_point INT,
    lead_time_days INT,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE risk_scores (
    risk_id SERIAL PRIMARY KEY,
    supplier_id INT REFERENCES suppliers(supplier_id),
    score_type TEXT NOT NULL,
    score_value NUMERIC(5,2),
    reason TEXT,
    computed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE simulations (
    simulation_id SERIAL PRIMARY KEY,
    scenario_type TEXT NOT NULL,
    scenario_name TEXT NOT NULL,
    payload JSONB,
    impact_revenue NUMERIC(12,2),
    impact_inventory NUMERIC(12,2),
    impact_delay NUMERIC(5,2),
    impact_service NUMERIC(5,2),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
