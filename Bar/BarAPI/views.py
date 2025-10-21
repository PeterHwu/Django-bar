# from django.shortcuts import render
from decimal import Decimal
from django.contrib.auth.models import User, Group

from .serializers import ManagerSerializer, MenuItemSerializer, CategorySerializer, CartSerializer, OrderSerializer
from .models import MenuItem, Category, Cart, Order, OrderItem

from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, BasePermission, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
# Create your views here.

def get_cart_by_user(request, user):
    user = request.user
    cart = Cart.objects.all()
    if user.groups.filter(name='Customer').exists():
        user_cart = cart.filter(user=user)
    else:
        return Response({"error": "User is not customer"}, status=status.HTTP_401_UNAUTHORIZED)
    # if no username return all carts
    if user_cart.count() == 0:
        return Response({"message": f"Cart of {user.username} is empty"}, status=status.HTTP_204_NO_CONTENT)
    serializer = CartSerializer(user_cart, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Customer').exists()

class ManagerGroupsView(viewsets.ModelViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    # request staff for GET, staff or superuser for the rest
    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [IsAdminUser | IsSuperUser]
        return super().get_permissions()
    
    # get list of users in any group
    def get(self, request):
        try:
            group_name = request.query_params.get('group_name')
            
            if not group_name:
                return Response({"error": "Group name parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            group_name = group_name.title()

            if Group.objects.filter(name=group_name).exists():
                pass
            else:
                return Response({"error": "Group does not exist"}, status=status.HTTP_204_NO_CONTENT)
            
            one_group  = Group.objects.get(name=group_name) # get the group object
            groupMembers = User.objects.filter(groups=one_group) # get all users in that group

            if len(groupMembers) == 0:
                return Response({"message": "No group members found"}, status=status.HTTP_204_NO_CONTENT)
            serializer = ManagerSerializer(groupMembers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_204_NO_CONTENT)
    # add or create a user to Manager group
    def post(self, request):
        try:
            username = request.data.get('username')
            user= User.objects.get(username=username)
            if not user:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            manager_group, _ = Group.objects.get_or_create(name='Manager')
            manager_group.user_set.add(user)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": f"User {username} added to Manager group"}, status=status.HTTP_200_OK)
    
    def delete(self, request):
        try:
            username = request.data.get('username')
            user= User.objects.get(username=username)
            if not user:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.remove(user)
        except Group.DoesNotExist:
            return Response({"error": "Manager group does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": f"User {username} removed from Manager group"}, status=status.HTTP_200_OK)
# end ManagerGroupsView class

class MenuItemsPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def menuItemsView(request):
    if request.method == 'GET':
        if not request.user.groups.filter(name__in=['Customer']).exists():
            return Response({"error": "Only customers can view menu items"}, status=status.HTTP_403_FORBIDDEN)
        
        menu_items = MenuItem.objects.all()
        # ordering by price
        if request.query_params.get('ordering'):
            ordering_param = request.query_params.get('ordering')
            if ordering_param not in ['price', '-price']:
                return Response({"error": "Invalid ordering parameter. Use 'price' or '-price'."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                menu_items = menu_items.order_by(ordering_param)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        paginator = MenuItemsPagination()
        # query by category
        if request.query_params.get('category_name'):
            category_name = request.query_params.get('category_name')
            menu_items = menu_items.filter(category__title__iexact=category_name)
            if not menu_items:
                return Response({"message": f"category: '{category_name}' does not exist"}, status=status.HTTP_404_NOT_FOUND)
            serializer = MenuItemSerializer(menu_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Check for page_size and page query parameters
        if request.query_params.get('page_size'):
            paginator.page_size = request.query_params.get('page_size')
        if request.query_params.get('page'):
            page = paginator.paginate_queryset(menu_items, request)
            if page is not None:
                serializer = MenuItemSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        else:
            serializer = MenuItemSerializer(menu_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    elif request.method == 'POST':
        user = request.user
        if not user.groups.filter(name='Manager').exists():
            return Response({"error": "Only managers can create menu items"}, status=status.HTTP_403_FORBIDDEN)
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
# end MenuItemsView

class CategoryView(viewsets.ModelViewSet):
    """List all categories or create a new category"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def list(self, request, *args, **kwargs):
        categories = self.get_queryset()
        if not categories:
            return Response({"error": "Category list is empty"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

# end CategoryView

class ManagerGroupDeliveryCrewView(viewsets.ModelViewSet):
    """Manger can add users to Delivery crew group"""
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [IsAdminUser | IsSuperUser]
        return super().get_permissions()
    
    def post(self, request):
        try:
            username = request.data.get('username')
            user= User.objects.get(username=username)
            if not user:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            group = Group.objects.get(name='Delivery')
            if group.user_set.contains(user):
                return Response({"message": f'User {username} is already in delivery crew'}, status=status.HTTP_200_OK)
            group.user_set.add(user)
            return Response({"message": f'User {username} assigned to delivery crew'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f'failed to assign user to delivery crew with error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# end ManagerGroupDeliveryCrewView class

class CartItemView(viewsets.ModelViewSet):
    # only customers can create cart
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    # anyone can get cart list
    def get(self, request):
        user = request.user
        return get_cart_by_user(request, user)

    def post(self, request):
        username = request.data.get('username')
        
        # Retrieve the user by username
        try:
            user = request.user
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get data from request
        menuitem_id = request.data.get('menuitem_id') 
        quantity = request.data.get('quantity')
        print(f'menuitem_id: {menuitem_id}, quantity: {quantity}')
        # Validate the inputs
        if not menuitem_id or not quantity:
            return Response({"error": "menuitem_id and quantity are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if MenuItem.objects.filter(id=menuitem_id).exists() is False:
            return Response({"error": "Menu item does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # if cart item already exists, update it
        if Cart.objects.filter(user=user, menuitem__id=menuitem_id).exists():
            cart_item = Cart.objects.get(user=user, menuitem__id=menuitem_id)
            cart_item.quantity += int(quantity)
            cart_item.price = cart_item.unit_price * cart_item.quantity
            cart_item.save()
            serializer = CartSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # if not exists, create new cart item
        try:
            # Get the MenuItem object
            menuitem = MenuItem.objects.get(id=menuitem_id)
            unit_price = menuitem.price
            price = unit_price * int(quantity)

            # Get or create the cart item
            cart_item = Cart.objects.create(
                user=user,
                menuitem=menuitem,
                quantity=quantity,
                unit_price=unit_price,
                price=price,
            )

            cart_item.save()
            serializer = CartSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except MenuItem.DoesNotExist:
            return Response({"error": "Failed to create cart item"}, status=status.HTTP_400_BAD_REQUEST)
# end CartItemView class

# customer can create order
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def placeOrderView(request):
    if request.method == 'POST':
        user = request.user
        if not user.groups.filter(name='Customer').exists():
            return Response({"error": "Only customers can view their orders"}, status=status.HTTP_403_FORBIDDEN)
        
        # create new order for the user
        from django.utils import timezone
        try:
            new_order = Order.objects.create(
                user=user,
                delivery_crew=None,
                status = False,
                total=0,
                date = timezone.now().date()
            )

            if new_order is None:
                return Response({"error": "Failed to create order"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            user_cart_list = get_cart_by_user(request, user).data
            print(f'user_cart_list: {user_cart_list}')
            for cart_item in user_cart_list:
                menuite_id = cart_item['menuitem']['id']
                quantity = cart_item['quantity']
                unit_price = cart_item['unit_price']
                price = cart_item['price']

                price = Decimal(price)
                unit_price = Decimal(unit_price)

                order_item = OrderItem.objects.create(
                    order = new_order,
                    menuitem = MenuItem.objects.get(id=menuite_id),
                    quantity = quantity,
                    unit_price = unit_price,
                    price = price
                )
                if order_item is None:
                    return Response({"error": "Failed to create order item"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                order_item.save()
                new_order.total += price

            # endfor cart_item
            new_order.save()

            return Response({"message": f"Order for '{user.username}' created successfully with id '{new_order.id}'"}, status=status.HTTP_201_CREATED)
        #TODO clean cart item after payment success
        except Exception as e:
            return Response({"error": f"Failed to create final order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# end OrderView function

# manager can assign order to delivery crew

@api_view(['POST'])
@permission_classes([IsAdminUser | IsSuperUser])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def assignDeliveryCrewToOrderView(request):
    if request.method == 'POST':
        username = request.data.get('order_username')
        user = User.objects.get(username=username)
        if not user:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        latest_order = Order.objects.filter(user=user).order_by('-date').first()
        if not latest_order:
            return Response({"error": f"No orders found for user {user.username}"}, status=status.HTTP_404_NOT_FOUND)
        
        delivery_crew_name = request.data.get('delivery_crew_username')
        if not delivery_crew_name:
            return Response({"error": "Delivery crew username is required"}, status=status.HTTP_400_BAD_REQUEST)
        delivery_crew_user = User.objects.get(username=delivery_crew_name)
        if not delivery_crew_user:
            return Response({"error": f"Delivery crew user'{delivery_crew_name}' does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        latest_order.delivery_crew = delivery_crew_user
        latest_order.save()
        return Response({"message": f"Order '{latest_order.id}' of user '{user.username}' assigned to delivery crew '{delivery_crew_name}'"}, status=status.HTTP_200_OK)
# end AssignOrderView function


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def customerOrderListView(request):
    """ get all orders of a customer """
    if request.method == 'GET':
        user = request.user
        if not user.groups.filter(name='Customer').exists():
            return Response({"error": "Only customers can view their orders"}, status=status.HTTP_403_FORBIDDEN)
        
        orders = Order.objects.filter(user=user)
        if not orders:
            return Response({"message": "No orders found"}, status=status.HTTP_204_NO_CONTENT)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

from rest_framework.exceptions import NotFound

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def deliveryCrewCheckOrUpdateOrderStatusView(request, order_id):
    """ Delivery crew can view and update order status assigned to them """
    delivery_user = request.user
    
    # Ensure user is a member of the 'Delivery' group
    if not delivery_user.groups.filter(name='Delivery').exists():
        return Response({"error": "Only delivery crew can view their assigned orders"}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        # Fetch the orders assigned to the delivery user
        assigned_orders = Order.objects.filter(delivery_crew=delivery_user)
        if not assigned_orders.exists():
            return Response({"message": "No assigned orders found"}, status=status.HTTP_204_NO_CONTENT)
        
        # Serialize the orders
        serializer = OrderSerializer(assigned_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PATCH':
        # Retrieve order username from the request
        order_instance = Order.objects.filter(pk=order_id)
        if not order_instance.exists():
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Update order status and save it
        new_status = request.data.get('status')
        if new_status is None:
            return Response({"error": "Status field is required"}, status=status.HTTP_400_BAD_REQUEST)
        order_instance.status = new_status
        order_instance.save()

        # Serialize and return the updated order
        serializer = OrderSerializer(order_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser | IsSuperUser])
@throttle_classes([UserRateThrottle])
def managerUpdateMenuItemView(request, menuitem_id):
    if request.method == 'PUT':
        user = request.user
        if not user.groups.filter(name='Manager').exists():
            return Response({"error": "Only managers can update menu items"}, status=status.HTTP_403_FORBIDDEN)
        try:
            menu_item_obj = MenuItem.objects.get(id=menuitem_id)
            serializer = MenuItemSerializer(menu_item_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except MenuItem.DoesNotExist:
            return Response({"error": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'PATCH':
        user = request.user
        if not user.groups.filter(name='Manager').exists():
            return Response({"error": "Only managers can update menu items"}, status=status.HTTP_403_FORBIDDEN)
        try:
            menu_item_obj = MenuItem.objects.get(id=menuitem_id)
            status = request.data.get('status')
            if status is None:
                return Response({"error": "Status field is required"}, status=status.HTTP_400_BAD_REQUEST)
            menu_item_obj.featured = status
            menu_item_obj.save()
            serializer = MenuItemSerializer(menu_item_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MenuItem.DoesNotExist:
            return Response({"error": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
# end managerUpdateMenuItemView function
