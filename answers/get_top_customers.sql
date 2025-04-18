SELECT customer_name, SUM(order_total) AS total_spent
FROM customers
JOIN orders ON customers.customer_id = orders.customer_id
GROUP BY customer_name
ORDER BY total_spent DESC
LIMIT 3;
