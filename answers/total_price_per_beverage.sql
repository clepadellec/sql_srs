SELECT beverage, SUM(food_price) AS total_price
FROM beverages
JOIN food_items ON 1=1  -- Assuming cross join-like behavior
GROUP BY beverage;
