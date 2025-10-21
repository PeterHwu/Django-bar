# Bar Models

This document describes the Django models used by the Little Lemon API (in `LittleLemonAPI/models.py`).

## Category

- id: AutoField (primary key)
- slug: SlugField (required)
- title: CharField(max_length=255)

String representation: `title`

## MenuItem

- id: AutoField
- title: CharField(max_length=255)
- price: DecimalField(max_digits=6, decimal_places=2)
- featured: BooleanField
- category: ForeignKey to `Category` (on_delete=PROTECT)

String representation: `title`

## Cart

- id: AutoField
- user: ForeignKey to `auth.User` (on_delete=CASCADE)
- menuitem: ForeignKey to `MenuItem` (on_delete=CASCADE)
- quantity: SmallIntegerField
- unit_price: DecimalField(max_digits=6, decimal_places=2)
- price: DecimalField(max_digits=6, decimal_places=2)

Unique constraint: (`menuitem`, `user`)
String representation: `{username}__{menuitem.title}`

## Order

- id: AutoField
- user: ForeignKey to `auth.User` (on_delete=CASCADE)
- delivery_crew: ForeignKey to `auth.User` (on_delete=SET_NULL, null=True, related_name='delivery_crew')
- status: BooleanField (indexed)
- total: DecimalField(max_digits=6, decimal_places=2)
- date: DateField

String representation: `order_{id}__{username}`

## OrderItem

- id: AutoField
- order: ForeignKey to `Order` (on_delete=CASCADE)
- menuitem: ForeignKey to `MenuItem` (on_delete=CASCADE)
- quantity: SmallIntegerField
- unit_price: DecimalField(max_digits=6, decimal_places=2)
- price: DecimalField(max_digits=6, decimal_places=2)

Unique constraint: (`order`, `menuitem`)
