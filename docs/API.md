# API Documentation

## Base URL
http://localhost:4000

## Overview endpoints
- GET /health
- GET /api/dashboard/overview
- GET /api/dashboard/trends
- GET /api/categories
- GET /api/regions

## Seller endpoints
- GET /api/sellers
- GET /api/sellers/:id
- GET /api/sellers/:id/performance
- GET /api/sellers/:id/trends
- GET /api/sellers/:id/reviews
- GET /api/sellers/:id/returns
- GET /api/sellers/risk

## Report endpoints
- GET /api/reports
- POST /api/reports/export

## Query parameters
- search
- category
- region
- risk
- startDate
- endDate
- page
- limit
- sort

## Response shape
The API returns consistent JSON payloads with success statuses or error messages, and uses validation for malformed requests.
