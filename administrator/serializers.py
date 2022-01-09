from rest_framework import serializers
from core.models import Order, OrderItem, Product, Link


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class LinkSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField('get_orders')

    def get_orders(self, obj):
        return OrderSerializer(Order.objects.filter(code=obj.code), many=True).data

    class Meta:
        model = Link
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    ambassador_revenue = serializers.ReadOnlyField()
    admin_revenue = serializers.ReadOnlyField()
    total = serializers.SerializerMethodField('get_total')
    order_items = OrderItemSerializer(many=True)

    def get_total(self, obj):
        items = OrderItem.objects.filter(order_id=obj.id)
        return sum((o.price * o.quantity) for o in items)

    class Meta:
        model = Order
        fields = '__all__'
