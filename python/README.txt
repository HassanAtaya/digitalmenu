Digital Menu API — Multi-Restaurant

Setup
1) Create a PostgreSQL database (defaults in .env or environment):
   - POSTGRES_HOST=localhost
   - POSTGRES_PORT=5432
   - POSTGRES_DB=digital_menu
   - POSTGRES_USER=postgres
   - POSTGRES_PASSWORD=postgres

2) Install dependencies:
   pip install -r requirements.txt

3) Run migrations:
   alembic upgrade head

4) Start the API:
   python run.py

Seeds
- Admin user: admin / evolusys
- Demo restaurant: name "La Famiglia"
  - Manager: username "lafamiglia", password "secret"

Key Endpoints
- Auth: POST /api/login (form fields username, password)
- Admin Restaurants:
  - GET /api/admin/restaurants
  - POST /api/admin/restaurants
  - GET /api/admin/restaurants/{id_or_slug}
  - PUT /api/admin/restaurants/{id_or_slug}
  - DELETE /api/admin/restaurants/{id_or_slug}
  - POST /api/admin/restaurants/{id_or_slug}/toggle-active
- Restaurant-scoped CRUD (admin or manager of that restaurant):
  - Settings:    /api/restaurants/{slug}/settings (+ /logo, + /barcode_image)
  - Categories:  /api/restaurants/{slug}/categories
  - Products:    /api/restaurants/{slug}/products
  - Ingredients: /api/restaurants/{slug}/ingredients
- Public menu JSON:
  - GET /api/public/menu/{restaurant_slug}

Public URL
- The Angular app should render the public menu at: http://<HOST>:<PORT>/{restaurant_slug}
- Example: http://127.0.0.1:4200/la-famiglia
