# Bibulous Frontend

This directory houses the frontend code for Bibulous, a Next.js 15+ application configured with modern glassmorphism UI elements, dark mode, and highly aesthetic recommendation carousels.

This project is bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Requirements
Ensure you have installed:
- Node.js >= 18.x
- npm >= 9.x (or yarn / pnpm equivalents)

## Getting Started

First, install the required node modules:

```bash
npm install
```

Since the frontend relies heavily on the FastAPI Python engine to deliver recommendations, **you must ensure the backend is running at http://localhost:8000 before proceeding.**

Next, start the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Architecture

- `src/app/page.tsx`: Initial sign-up and onboarding selection flow.
- `src/app/home/page.tsx`: Primary "Top Picks" dynamic dashboard.
- `src/app/book/[isbn]/page.tsx`: Specific book detail views with built-in nested similarity carousels.
- `src/components/`: Reusable stylized components like `BookCard.tsx` and `Navbar.tsx`.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.
