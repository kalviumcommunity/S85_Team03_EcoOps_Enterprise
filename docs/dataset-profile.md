# Dataset Profile

## 1. Overview

The Seller Trust Analytics Platform uses a synthetic e-commerce dataset consisting of four relational CSV files. Together, these files represent sellers, users, products, and customer interactions within an online marketplace.

The dataset is designed to support seller performance analysis, customer behaviour analysis, product analytics, and seller trust evaluation.

---

# 2. Dataset Summary

| File             | Description                                                                            |
| ---------------- | -------------------------------------------------------------------------------------- |
| sellers.csv      | Contains seller information and quality scores.                                        |
| users.csv        | Contains customer information and behavioural attributes.                              |
| products.csv     | Contains product details, pricing, categories, and quality scores.                     |
| interactions.csv | Records user interactions with sellers and products, including ratings and timestamps. |

---

# 3. Dataset Relationships

The dataset follows a relational structure.

* **users.csv** connects to **interactions.csv** using `user_id`.
* **sellers.csv** connects to **interactions.csv** using `seller_id`.
* **products.csv** connects to **interactions.csv** using `product_id`.

The `interactions.csv` file acts as the primary fact table for analytical processing.

---

# 4. File Descriptions

## sellers.csv

Stores seller-level information.

| Column    | Description                                                       |
| --------- | ----------------------------------------------------------------- |
| seller_id | Unique seller identifier                                          |
| quality   | Seller quality score representing reliability and service quality |

Business Purpose:

* Seller trust analysis
* Seller ranking
* Performance comparison

---

## users.csv

Stores customer information.

| Column            | Description                      |
| ----------------- | -------------------------------- |
| user_id           | Unique customer identifier       |
| loyalty           | Customer loyalty score           |
| price_sensitivity | Customer price sensitivity score |

Business Purpose:

* Customer segmentation
* Behaviour analysis

---

## products.csv

Stores product information.

| Column        | Description                        |
| ------------- | ---------------------------------- |
| product_id    | Unique product identifier          |
| seller        | Seller responsible for the product |
| category      | Product category                   |
| price         | Product price                      |
| final_quality | Product quality score              |
| rating_count  | Number of customer ratings         |

Business Purpose:

* Product performance analysis
* Category analytics
* Pricing insights

---

## interactions.csv

Stores marketplace interaction events.

| Column     | Description               |
| ---------- | ------------------------- |
| user_id    | Customer identifier       |
| product_id | Product identifier        |
| seller_id  | Seller identifier         |
| category   | Product category          |
| price      | Product price             |
| action     | Customer interaction type |
| rating     | Customer rating           |
| timestamp  | Interaction date and time |

Business Purpose:

* Seller trust analytics
* Customer behaviour analysis
* KPI calculation
* Time-based analysis

---

# 5. Primary Keys

| File             | Primary Key                                 |
| ---------------- | ------------------------------------------- |
| sellers.csv      | seller_id                                   |
| users.csv        | user_id                                     |
| products.csv     | product_id                                  |
| interactions.csv | No single primary key (interaction records) |

---

# 6. Data Quality Observations

Initial observations from the dataset:

* The dataset follows a relational design.
* Identifier columns are consistently used across files.
* Missing values are expected in the `rating` column because not every interaction includes customer feedback.
* Timestamp values will require conversion to datetime format during preprocessing.
* No major structural issues were identified during the initial review.

---

# 7. Business Insights

This dataset supports the following business questions:

* Which sellers have the highest quality scores?
* Which sellers receive the highest customer ratings?
* Which product categories perform best?
* How do customer interactions change over time?
* Which customers demonstrate higher loyalty?
* How does seller quality influence customer ratings?

---

# 8. Preprocessing Requirements

Before analysis, the following preprocessing tasks will be performed:

* Convert timestamp values into datetime format.
* Validate data types for all columns.
* Handle missing values in the rating column appropriately.
* Remove duplicate records if identified.
* Verify relationships between the four datasets.
* Prepare clean datasets for analytical processing.

---

# 9. Expected Outputs

The cleaned dataset will support:

* Seller Trust Dashboard
* Product Analytics Dashboard
* Customer Behaviour Dashboard
* KPI Reporting
* Time-Series Analysis
* Seller Ranking
* Business Intelligence Reporting

---

# 10. Conclusion

The dataset is well-structured and suitable for developing the Seller Trust Analytics Platform. Its relational design closely resembles a production e-commerce database and provides sufficient information to build meaningful seller trust metrics, customer behaviour insights, and interactive business dashboards.
