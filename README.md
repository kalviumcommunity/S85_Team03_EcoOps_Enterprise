# Seller Trust Analytics Platform

STAP is a full-stack marketplace operations application for monitoring seller quality, calculating trust, finding risk, exploring historical performance, and exporting reports.

## Features

- Live marketplace KPI dashboard
- Seller search, filtering, sorting, and pagination
- Seller detail analytics with historical charts and trust contribution
- High-risk intervention queue with risk drivers
- Marketplace trend analysis
- CSV, Excel, and PDF exports
- Loading, empty, API error, and retry states
- PostgreSQL persistence through Prisma

## Architecture

```text
PostgreSQL -> Prisma -> Express/TypeScript API -> Axios -> React/Vite dashboard
```

The backend owns all analytics calculations. The React application consumes REST responses and does not use mock business data.

## Tech stack

- Frontend: React, TypeScript, Vite, React Router, Tailwind CSS, Recharts, Axios
- Backend: Node.js, Express, TypeScript, Zod
- Database: PostgreSQL, Prisma
- Reports: CSV, ExcelJS, PDFKit

## Trust score

Each seller receives a score from 0 to 100:

```text
Rating              25%
Return rate         20%
Review sentiment    20%
Delivery            20%
Consistency         15%
```

Risk classification is configurable in the backend analytics layer:

- 85–100: Healthy
- 70–84: Under Monitoring
- 0–69: High Risk

Marketplace health is calculated from aggregate trust, risk distribution, rating, returns, delivery, and sentiment metrics.

## Requirements

- Node.js 20+
- PostgreSQL 16+, or Docker Desktop
- npm

## Quick start

```powershell
npm install
npm run dev
```

Then open http://localhost:5173.

The root `npm run dev` command starts PostgreSQL automatically if it is not already running, starts the backend API on http://localhost:4000, and starts the frontend on http://localhost:5173.

### Environment variables

Copy the project example files if needed:

```powershell
Copy-Item .env.example backend/.env
Copy-Item frontend/.env.example frontend/.env
```

The app expects:

- `DATABASE_URL` = PostgreSQL connection string
- `PORT` = backend port (default `4000`)
- `FRONTEND_URL` = frontend origin for CORS
- `VITE_API_URL` = frontend API base URL

The default dev setup uses PostgreSQL on `localhost:5000` via Docker Compose.

## Database migration and seed

```powershell
npm run db:migrate
npm run db:seed
```

The seed generates 120 sellers, 600 products, 5,000 orders, 2,500 reviews, 600 returns, and eight historical performance records per seller.

## Manual local run

If you want to run each process separately:

```powershell
cd backend
npm run dev
```

```powershell
cd frontend
npm run dev
```

## Docker

Docker Desktop must be running first for the automatic database startup path:

```powershell
docker compose up -d postgres
```

The development startup script does this automatically when required and does not reset your database.

## API

See [docs/API.md](docs/API.md) for endpoint details. Main routes include `/api/dashboard/overview`, `/api/dashboard/trends`, `/api/sellers`, `/api/sellers/:id`, `/api/sellers/risk`, and `/api/reports/export`.

## Reports

The Reports screen downloads seller analytics as CSV, XLSX, or PDF using the backend export endpoint.

## Testing and builds

```powershell
cd backend
npm test
npm run build
cd ../frontend
npm run build
npm run lint
```

## Documentation

- [docs/PRD.md](docs/PRD.md)
- [docs/SRS.md](docs/SRS.md)
- [docs/Architecture.md](docs/Architecture.md)
- [docs/Database.md](docs/Database.md)
- [docs/API.md](docs/API.md)

## Screenshots

Add screenshots of the dashboard and seller detail views here after local database setup.

## Future improvements

Authentication, persistent scoring configuration, scheduled refreshes, alerting, predictive risk analysis, and marketplace integrations are natural next steps.

## Contributing

Create a focused feature branch, keep analytics in the backend layer, add tests for behavior changes, and run the backend/frontend checks before opening a pull request.
