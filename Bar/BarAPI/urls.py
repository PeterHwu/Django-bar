from django.urls import path
from .views import (ManagerGroupsView, 
                    menuItemsView, 
                    CategoryView, 
                    # ManagerGroupDeliveryCrewView, 
                    CartItemView,
                    assignDeliveryCrewToOrderView,
                    customerOrderListView,
                    deliveryCrewCheckOrUpdateOrderStatusView,
                    managerUpdateMenuItemView,
                    placeOrderView)
urlpatterns = [
    path('groups/manager/users', ManagerGroupsView.as_view({
        'get': 'get',
        'post': 'post',
        'delete': 'delete',
    }), name='manager-users'),
    path('menu-items', menuItemsView, name='menu-items'),
    path('categories', CategoryView.as_view({
        'get': 'list', 
        'post': 'create',
        }), name='categories'),
    # path('groups/manager/delivery', ManagerGroupDeliveryCrewView.as_view({ 
    #     'post': 'post',
    # }), name='manager-delivery-crew'),
    path('cart/menu-items', CartItemView.as_view({
        'get': 'get',
    }), name='cart-management'),
    path('cart/menu-items', CartItemView.as_view({'post': 'post'}), name='add-cart-item'),
    path('assign-delivery-crew', assignDeliveryCrewToOrderView, name='assign-delivery-crew'),
    path('cart/orders', customerOrderListView, name='customer-orders'),
    path('cart/orders', placeOrderView, name='place-order'),
    path('orders', deliveryCrewCheckOrUpdateOrderStatusView, name='delivery-crew-orders'),
    path('orders/<int:order_id>', deliveryCrewCheckOrUpdateOrderStatusView, name='delivery-crew-orders'),
    path('menu-items/<int:menuitem_id>', managerUpdateMenuItemView, name='manager-update-menu-item'),

]