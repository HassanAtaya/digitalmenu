Digital Menu — Multi-Restaurant Edition

Overview
- FastAPI + SQLAlchemy + Alembic backend in `python/`
- Angular 19 + PrimeNG + Tailwind frontend in `angular/`
- Supports multiple restaurants with public menus at `http://<HOST>:<PORT>/<restaurant_slug>`

Backend — Setup and Run
1) Create a PostgreSQL database and export env vars (or use defaults):
   - POSTGRES_HOST=localhost
   - POSTGRES_PORT=5432
   - POSTGRES_DB=digital_menu
   - POSTGRES_USER=postgres
   - POSTGRES_PASSWORD=postgres
2) Install deps:
   cd python && pip install -r requirements.txt
3) Run migrations:
   alembic upgrade head
4) Start API:
   python run.py
   - API base: http://127.0.0.1:8000/api

Seeds
- Admin user: admin / evolusys
- Demo restaurant: name "La Famiglia" (slug: la-famiglia)
  - Manager: username "lafamiglia", password "secret"

Frontend — Setup and Run
1) In another terminal:
   cd angular
   npm install
   npm start
   - App: http://127.0.0.1:4200

Usage
- Login (admin): http://127.0.0.1:4200/login → admin/evolusys
  - Redirect to /restaurant (admin list). Add/Edit/Delete restaurants, toggle active, open/copy public URL.
- Login (manager): use the restaurant credentials → redirects to /restaurant/<slug>/edit workspace.
- Public Menu: http://127.0.0.1:4200/<restaurant_slug>
  - Example: http://127.0.0.1:4200/la-famiglia

Notes
- Deletions are blocked if in-use:
  - Category: cannot delete if products linked
  - Restaurant: cannot delete if it has categories/products/ingredients
- Prices: only `price_currency_1` stored; `price_currency_2` computed from settings rate
- Slugs: auto-generated from name; unique and immutable


