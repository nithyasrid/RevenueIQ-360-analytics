-- PostgreSQL: run after loading data/transactions.csv into retail_orders.
-- Revenue recognition: completed orders only.
CREATE TABLE IF NOT EXISTS retail_orders (
 order_id INTEGER PRIMARY KEY, order_date DATE NOT NULL, customer_id INTEGER NOT NULL,
 product_id INTEGER NOT NULL, category TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity>0),
 unit_price NUMERIC(12,2) NOT NULL, unit_cost NUMERIC(12,2) NOT NULL,
 discount_pct NUMERIC(5,2) NOT NULL CHECK(discount_pct BETWEEN 0 AND 100),
 status TEXT NOT NULL, region TEXT NOT NULL
);
-- In psql from repository root: \copy retail_orders FROM 'data/transactions.csv' WITH (FORMAT csv, HEADER true)

-- Monthly revenue, month-over-month growth (window function)
WITH monthly AS (
 SELECT date_trunc('month',order_date)::date AS month,
 SUM(CASE WHEN status='Completed' THEN quantity*unit_price*(1-discount_pct/100) ELSE 0 END) AS revenue
 FROM retail_orders GROUP BY 1
), growth AS (
 SELECT month,revenue,LAG(revenue) OVER(ORDER BY month) AS prior_month FROM monthly
)
SELECT month,ROUND(revenue,2) AS revenue,
 ROUND(100*(revenue-prior_month)/NULLIF(prior_month,0),2) AS mom_growth_pct
FROM growth ORDER BY month;

-- Customer RFM features
WITH orders AS (
 SELECT customer_id,order_id,order_date,quantity*unit_price*(1-discount_pct/100) AS net_sales
 FROM retail_orders WHERE status='Completed'
)
SELECT customer_id, ((SELECT MAX(order_date) FROM retail_orders WHERE status='Completed') - MAX(order_date)) AS recency_days,
 COUNT(DISTINCT order_id) AS frequency,ROUND(SUM(net_sales),2) AS monetary
FROM orders GROUP BY customer_id ORDER BY monetary DESC;

-- Monthly cohort retention (distinct customers)
WITH active AS (
 SELECT DISTINCT customer_id,date_trunc('month',order_date)::date AS month
 FROM retail_orders WHERE status='Completed'
), cohorts AS (
 SELECT customer_id,month,MIN(month) OVER(PARTITION BY customer_id) AS cohort_month FROM active
), cohort_counts AS (
 SELECT cohort_month,
 (EXTRACT(YEAR FROM age(month,cohort_month))*12+EXTRACT(MONTH FROM age(month,cohort_month)))::int AS month_number,
 COUNT(DISTINCT customer_id) AS active_customers FROM cohorts GROUP BY 1,2
)
SELECT cohort_month,month_number,active_customers,
 ROUND(100.0*active_customers/NULLIF(MAX(active_customers) FILTER(WHERE month_number=0) OVER(PARTITION BY cohort_month),0),2) AS retention_pct
FROM cohort_counts ORDER BY cohort_month,month_number;

-- Category margin: product cost only, not fully loaded profitability
SELECT category,
 ROUND(SUM(CASE WHEN status='Completed' THEN quantity*unit_price*(1-discount_pct/100) ELSE 0 END),2) AS revenue,
 ROUND(SUM(CASE WHEN status='Completed' THEN quantity*(unit_price*(1-discount_pct/100)-unit_cost) ELSE 0 END),2) AS product_profit
FROM retail_orders GROUP BY category ORDER BY product_profit DESC;
