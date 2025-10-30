from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'product_name', 'amount', 'status']
        read_only_fields = ['id', 'status']


class PaymeLinkRequestSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=False)
    product_name = serializers.CharField(required=False, max_length=255)
    amount = serializers.DecimalField(required=False, max_digits=12, decimal_places=2)
    return_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    def validate(self, attrs):
        order_id = attrs.get('order_id')
        product_name = attrs.get('product_name')
        amount = attrs.get('amount')

        if not order_id and (product_name is None or amount is None):
            raise serializers.ValidationError('Provide order_id or product_name and amount.')

        if amount is not None and amount <= 0:
            raise serializers.ValidationError({'amount': 'Must be greater than 0.'})

        return attrs


class PaymeLinkByOrderSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
    return_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)


class PaymeLinkNewOrderSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    return_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Must be greater than 0.')
        return value


