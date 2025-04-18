SELECT customers.customer_name, orders.order_total
FROM customers
JOIN orders ON customers.customer_id = orders.customer_id;
