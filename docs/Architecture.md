# Architecture

## Overview
The repository is organized as a small monorepo with a Node.js backend and a Vite React frontend. The backend uses Prisma to talk to PostgreSQL, and the frontend calls the REST API for all metrics and charts.

## Backend
- Express server with REST routes
- Zod validation for request inputs
- Prisma ORM and generated client
- Complex analytics in reusable service logic
- CSV/XLSX/PDF report generation utilities

## Frontend
- React routing for dashboard and seller views
- Recharts for interactive analytics visualization
- Axios for API communication
- Tailwind CSS for enterprise styling

## Data flow
1. Generate realistic synthetic data in a seed script.
2. Store the data in PostgreSQL using Prisma schema models.
3. Query aggregated metrics from the backend analytics layer.
4. Serve structured JSON to the React dashboard.
5. Render KPI cards, charts, and report exports based on backend responses.
