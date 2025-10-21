from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'groups']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    # category = CategorySerializer()
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'category', 'featured']
        depth = 1

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(instance.category).data
        return representation

class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    menuitem = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['menuitem'] = MenuItemSerializer(instance.menuitem).data
        representation['user'] = instance.user.username
        return representation
    
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    delivery_crew = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.username
        if instance.delivery_crew:
            representation['delivery_crew'] = instance.delivery_crew.username
        else:
            representation['delivery_crew'] = None
        return representation

class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    menuitem = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['menuitem'] = MenuItemSerializer(instance.menuitem).data
        representation['order'] = instance.order.id
        return representation