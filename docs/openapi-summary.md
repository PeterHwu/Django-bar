# OpenAPI Summary (manual)

This is a short, machine-friendly summary of key endpoints to help if you want to generate an OpenAPI spec later.

Paths:
- /menu-items
  - GET: list menu items (Customer)
  - POST: create menu item (Manager)
- /menu-items/{menuitem_id}
  - PUT/PATCH: update menu item (Manager)
- /categories
  - GET: list categories
  - POST: create category
- /groups/manager/users
  - GET: list group members (Admin)
  - POST: add user to Manager (Admin/Superuser)
  - DELETE: remove user from Manager (Admin/Superuser)
- /cart/menu-items
  - GET: get/cart items for current customer
  - POST: add or update cart item
- /cart/orders
  - GET: list customer's orders
  - POST: create order (place order)
- /assign-delivery-crew
  - POST: assign delivery crew to latest order of a user (Admin/Superuser)
- /orders
  - GET: delivery crew gets assigned orders
- /orders/{order_id}
  - PATCH: delivery crew updates status

Suggested next step: run Django REST Framework automatic schema generation (e.g., drf-spectacular or coreapi) to produce a full OpenAPI JSON/YAML.
