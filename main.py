import sqlite3
import pandas as pd

# connect to database
conn = sqlite3.connect('data.sqlite')

# PART 1: JOIN & FILTER

# Boston employees 
df_boston = pd.read_sql("""
SELECT e.firstName, e.lastName
FROM employees e
JOIN offices o
ON e.officeCode = o.officeCode
WHERE o.city = 'Boston';
""", conn)

# Offices with zero employees
df_zero_emp = pd.read_sql("""
SELECT o.officeCode, o.city, o.state
FROM offices o
LEFT JOIN employees e
ON o.officeCode = e.officeCode
WHERE e.employeeNumber IS NULL;
""", conn)

# PART 2: TYPES OF JOIN

df_employee = pd.read_sql("""
SELECT e.firstName, e.lastName, o.city, o.state
FROM employees e
LEFT JOIN offices o
ON e.officeCode = o.officeCode
ORDER BY e.firstName, e.lastName;
""", conn)

df_contacts = pd.read_sql("""
SELECT c.contactFirstName, c.contactLastName, c.phone, c.salesRepEmployeeNumber
FROM customers c
LEFT JOIN orders o
ON c.customerNumber = o.customerNumber
WHERE o.customerNumber IS NULL
ORDER BY c.contactLastName;
""", conn)


# PART 3: BUILT-IN FUNCTION
df_payment = pd.read_sql("""
SELECT c.contactFirstName, c.contactLastName,
       p.amount, p.paymentDate
FROM customers c
JOIN payments p
ON c.customerNumber = p.customerNumber
ORDER BY CAST(p.amount AS REAL) DESC;
""", conn)

# PART 4: GROUP BY

df_credit = pd.read_sql("""
SELECT e.employeeNumber, e.firstName, e.lastName,
       COUNT(c.customerNumber) AS num_customers
FROM employees e
JOIN customers c
ON e.employeeNumber = c.salesRepEmployeeNumber
GROUP BY e.employeeNumber
HAVING AVG(c.creditLimit) > 90000
ORDER BY num_customers DESC;
""", conn)

df_product_sold = pd.read_sql("""
SELECT p.productName,
       COUNT(DISTINCT o.orderNumber) AS numorders,
       SUM(od.quantityOrdered) AS totalunits
FROM products p
JOIN orderdetails od
ON p.productCode = od.productCode
JOIN orders o
ON od.orderNumber = o.orderNumber
GROUP BY p.productCode
ORDER BY totalunits DESC;
""", conn)

# PART 5: MULTIPLE JOINS

df_total_customers = pd.read_sql("""
SELECT p.productName,
       p.productCode,
       COUNT(DISTINCT o.customerNumber) AS numpurchasers
FROM products p
JOIN orderdetails od
ON p.productCode = od.productCode
JOIN orders o
ON od.orderNumber = o.orderNumber
GROUP BY p.productCode
ORDER BY numpurchasers DESC;
""", conn)

df_customers = pd.read_sql("""
SELECT o.officeCode, o.city,
       COUNT(c.customerNumber) AS n_customers
FROM offices o
LEFT JOIN employees e
ON o.officeCode = e.officeCode
LEFT JOIN customers c
ON e.employeeNumber = c.salesRepEmployeeNumber
GROUP BY o.officeCode, o.city;
""", conn)

# PART 6: SUBQUERY

df_under_20 = pd.read_sql("""
SELECT DISTINCT
       e.employeeNumber, e.firstName, e.lastName,
       o.city, o.officeCode
FROM employees e
JOIN offices o       ON e.officeCode      = o.officeCode
JOIN customers c     ON e.employeeNumber  = c.salesRepEmployeeNumber
JOIN orders ord      ON c.customerNumber  = ord.customerNumber
JOIN orderdetails od ON ord.orderNumber   = od.orderNumber
WHERE od.productCode IN (
    SELECT p.productCode
    FROM products p
    JOIN orderdetails od2 ON p.productCode   = od2.productCode
    JOIN orders o2        ON od2.orderNumber = o2.orderNumber
    GROUP BY p.productCode
    HAVING COUNT(DISTINCT o2.customerNumber) < 20
)
ORDER BY e.employeeNumber
""", conn)

# close connection
conn.close()