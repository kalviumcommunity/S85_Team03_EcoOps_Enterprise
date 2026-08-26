# Product Requirements Document

## Product overview
The Seller Trust Analytics Platform (STAP) is designed to give marketplace teams a unified view of seller health, risk, and quality trends. It combines transaction, review, return, and fulfillment data into a single set of KPI cards and charts that support operational monitoring and business review.

## Goals
- Monitor overall marketplace health
- Detect sellers needing intervention
- Standardize trust scoring across all sellers
- Improve visibility into return and delivery issues
- Surface meaningful business insights and exportable reports

## Users
- Operations managers
- Seller quality analysts
- Business analysts
- Customer experience leads

## Functional requirements
1. Dashboard with KPI cards and risk distribution
2. Seller directory with search, filter, sort, and pagination
3. Seller detail pages showing trust metrics and history
4. Risk analytics with classification and trend monitoring
5. Report export to CSV, XLSX, and PDF
6. Business insight summaries derived from rules
7. Secure backend API with validation and error responses

## Non-functional requirements
- Real backend data source
- Validation for inputs
- Consistent JSON API responses
- Responsive analytics UI
- Use of PostgreSQL + Prisma for persistent storage
- Test coverage for trust scoring and risk behavior
