from rest_framework import serializers
from .models import OrderCheckoutUserInfo




class OrderCheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderCheckoutUserInfo
        fields = '__all__'
        read_only_fields = ['order_id', 'user', 'total_price', 'estimated_delivery_date']

    def create(self, validated_data):
        """
        Custom create method to handle automatic calculations for:
        - Total price
        - Estimated delivery date
        """
        request = self.context.get('request')
        user = request.user if request else None
        validated_data['user'] = user

        # Calculate total price
        product = validated_data['product']
        quantity = validated_data.get('quantity', 1)
        delivery_charges = validated_data.get('delivery_charges', 0)
        express_charge = 20 if validated_data.get('delivery_method') == 'express' else 0
        validated_data['total_price'] = product.price * quantity + delivery_charges + express_charge

        # Calculate estimate delivery date
        delivery_days = 2 if validated_data.get('delivery_method') == 'express' else 5
        validated_data['estimated_delivery_date'] = timezone.now().date() + timedelta(days=delivery_days)

        return super().create(validated_data)
