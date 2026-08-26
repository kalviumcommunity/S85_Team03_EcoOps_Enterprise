# Database

STAP uses PostgreSQL 16 with Prisma ORM.

## Models
- `Seller`: seller identity, region, category, and lifecycle status
- `Product`: seller catalog records
- `Order`: order and fulfillment events
- `Review`: ratings and sentiment labels
- `Return`: return events and reasons
- `SellerPerformance`: monthly historical score snapshots

## Local setup

Start PostgreSQL with Docker:

```powershell
docker compose up -d postgres
```

Set `DATABASE_URL` in `backend/.env`, then create the schema:

```powershell
cd backend
npx prisma migrate dev --name init
npm run seed
```

The seed creates 120 sellers, 600 products, 5,000 orders, 2,500 reviews, 600 returns, and eight historical performance records per seller.

## Useful commands

```powershell
npx prisma generate
npx prisma studio
npx prisma migrate status
```
