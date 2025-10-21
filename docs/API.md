# Little Lemon API Reference

This document describes the API endpoints, request parameters, and response shapes for the Little Lemon Django REST API implemented in `LittleLemonAPI`.

## Authentication
All endpoints require authentication (JWT or session), and many endpoints require the user to belong to specific groups: `Customer`, `Manager`, `Delivery`, or admin/superuser.

---

## Endpoints

### 1) GET /menu-items
- Description: Returns list of menu items. Only users in `Customer` group can view.
- Query parameters:
  - `category_name` (optional): filter by category title (case-insensitive exact match).
  - `ordering` (optional): `price` or `-price` to sort by price ascending/descending.
  - `page` (optional): page number for pagination.
  - `page_size` (optional): number of items per page.
- Response (200): array of MenuItem objects.

MenuItem shape:
- id: integer
- title: string
- price: string (decimal)
- featured: boolean
- category: { id, slug, title }

Example response:
{
  "id": 1,
  "title": "Margherita",
  "price": "9.99",
  "featured": false,
  "category": { "id": 2, "slug": "pizza", "title": "Pizza" }
}

---

### 2) POST /menu-items
- Description: Create a new menu item. Only users in `Manager` group.
- Body:
  - title: string (required)
  - price: decimal (required)
  - category: integer (category id) (required)
  - featured: boolean (optional)
- Response: 201 with created MenuItem object or 400 on validation.

---

### 3) GET /categories
- Description: List categories. Authenticated users.
- Response: 200 with array of categories
Category shape: { id, slug, title }

### 4) POST /categories
- Description: Create category. Authenticated users.
- Body: { slug, title }
- Response: 201 with created category

---

### 5) POST /groups/manager/users
### GET /groups/manager/users
### DELETE /groups/manager/users
- Description: Manage membership of the `Manager` group. Admin-only (staff) for GET, Admin or Superuser for POST/DELETE.
- Requests:
  - GET: query param `group_name` required to list users in a group.
  - POST body: { username }
  - DELETE body: { username }
- Responses: 200 on success with messages or serialized users for GET.

---

### 6) POST /cart/menu-items
- Description: Add an item to a customer's cart or update quantity if it exists. Authenticated customers only.
- Body: { menuitem_id: integer, quantity: integer }
- Response: 201 on creation with Cart object or 200 on update.

Cart shape (response):
- id: integer
- user: string (username)
- menuitem: MenuItem object
- quantity: integer
- unit_price: string
- price: string

---

### 7) GET /cart/menu-items
- Description: Get current authenticated customer's cart items. Authenticated customers only.
- Response: 200 with list of cart items or 204 if empty.

---

### 8) POST /cart/orders (place order)
- Description: Customers create an Order from their cart. Authenticated customers only.
- Body: none required. Creates an Order and OrderItem records out of the customer's cart.
- Response: 201 with message including order id on success.

---

### 9) GET /cart/orders
- Description: Customer can list their past orders. Authenticated customers only.
- Response: 200 with list of Order objects.

Order shape:
- id
- user: username
- delivery_crew: username or null
- status: boolean
- total: string
- date: YYYY-MM-DD

---

### 10) POST /assign-delivery-crew
- Description: Admins or superusers can assign a delivery crew user to the latest order of a given user.
- Body: { order_username: string, delivery_crew_username: string }
- Response: 200 with message on success.

---

### 11) GET /orders and PATCH /orders/<order_id>
- Description: Delivery crew can GET orders assigned to them; PATCH to update order status.
- Permissions: user must be in `Delivery` group to GET or PATCH.
- PATCH Body: { status: boolean }
- Responses: 200 with updated order or 204 if no assigned orders.

---

### 12) PUT/PATCH /menu-items/<menuitem_id>
- Description: Managers can update menu items. PUT expects full update (partial=True used), PATCH updates `featured` status when `status` provided.
- Permissions: Manager group for both; Admin/Superuser allowed.
- Body: fields of MenuItem to update
- Response: 200 with updated MenuItem.

---

## Notes and limitations
- Authentication method depends on your Django REST Framework config (session or token/JWT). Ensure `rest_framework` is set up in `settings.py`.
- Some views use group membership checks; ensure groups `Customer`, `Manager`, `Delivery` exist and users are assigned.
- Order placement currently does not clear the cart after creating order (TODO in code).


For a human-friendly overview of models, see `docs/models.md`.
