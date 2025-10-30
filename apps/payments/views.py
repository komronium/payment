from django.conf import settings
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers

from paytechuz.gateways.payme import PaymeGateway
from paytechuz.integrations.django.views import BasePaymeWebhookView

from .models import Order
from .serializers import (
    PaymeLinkRequestSerializer,
    PaymeLinkByOrderSerializer,
    PaymeLinkNewOrderSerializer,
    OrderSerializer,
)


class PaymeWebhookView(BasePaymeWebhookView):
    def successfully_payment(self, params, transaction):
        order = Order.objects.get(id=transaction.account_id)
        order.status = 'paid'
        order.save()

    def cancelled_payment(self, params, transaction):
        order = Order.objects.get(id=transaction.account_id)
        order.status = 'cancelled'
        order.save()


class PaymeCreateLinkView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        operation_id='create_payme_link',
        description='Create Payme payment link. If order_id is omitted, a new Order is created.',
        request=PaymeLinkRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='PaymeLinkResponse',
                    fields={
                        'payment_url': serializers.URLField(),
                        'order': OrderSerializer(),
                    },
                ),
                description='Payment link created',
            ),
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Order not found'),
        },
        tags=['payments'],
    )
    def post(self, request):
        serializer = PaymeLinkRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data.get('order_id')
        return_url = serializer.validated_data.get('return_url')

        if order_id:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            order = Order.objects.create(
                product_name=serializer.validated_data['product_name'],
                amount=serializer.validated_data['amount'],
                status='pending',
            )

        payme_conf = settings.PAYTECHUZ['PAYME']
        payme = PaymeGateway(
            payme_id=payme_conf['PAYME_ID'],
            payme_key=payme_conf['PAYME_KEY'],
            is_test_mode=payme_conf.get('IS_TEST_MODE', True),
        )

        amount_tiyin = int(Decimal(order.amount) * 100)
        link = payme.create_payment(
            id=order.id,
            amount=amount_tiyin,
            return_url=return_url,
        )

        return Response({'payment_url': link, 'order': OrderSerializer(order).data})


class PaymeCreateLinkByOrderView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        operation_id='create_payme_link_for_order',
        description='Create Payme link for an existing Order.',
        request=None,
        responses={200: OpenApiResponse(response=inline_serializer(name='PaymeLinkResponse', fields={'payment_url': serializers.URLField(), 'order': OrderSerializer()}))},
        tags=['payments'],
    )
    def post(self, request, order_id: int):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        payme_conf = settings.PAYTECHUZ['PAYME']
        payme = PaymeGateway(
            payme_id=payme_conf['PAYME_ID'],
            payme_key=payme_conf['PAYME_KEY'],
            is_test_mode=payme_conf.get('IS_TEST_MODE', True),
        )

        amount_tiyin = int(Decimal(order.amount) * 100)
        link = payme.create_payment(
            id=order.id,
            amount=amount_tiyin,
            return_url=request.data.get('return_url'),
        )

        return Response({'payment_url': link, 'order': OrderSerializer(order).data})


class PaymeCreateLinkNewOrderView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        operation_id='create_payme_link_new_order',
        description='Create a new Order and Payme link in one step.',
        request=PaymeLinkNewOrderSerializer,
        responses={200: OpenApiResponse(response=inline_serializer(name='PaymeLinkResponse', fields={'payment_url': serializers.URLField(), 'order': OrderSerializer()}))},
        tags=['payments'],
    )
    def post(self, request):
        serializer = PaymeLinkNewOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = Order.objects.create(
            product_name=serializer.validated_data['product_name'],
            amount=serializer.validated_data['amount'],
            status='pending',
        )

        payme_conf = settings.PAYTECHUZ['PAYME']
        payme = PaymeGateway(
            payme_id=payme_conf['PAYME_ID'],
            payme_key=payme_conf['PAYME_KEY'],
            is_test_mode=payme_conf.get('IS_TEST_MODE', True),
        )

        amount_tiyin = int(Decimal(order.amount) * 100)
        link = payme.create_payment(
            id=order.id,
            amount=amount_tiyin,
            return_url=serializer.validated_data.get('return_url'),
        )

        return Response({'payment_url': link, 'order': OrderSerializer(order).data})


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-id')
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=['orders'])
    def list(self, request, *args, **kwargs):  # type: ignore[override]
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=['orders'])
    def retrieve(self, request, *args, **kwargs):  # type: ignore[override]
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(tags=['orders'])
    def create(self, request, *args, **kwargs):  # type: ignore[override]
        return super().create(request, *args, **kwargs)

    @extend_schema(tags=['orders'])
    def update(self, request, *args, **kwargs):  # type: ignore[override]
        return super().update(request, *args, **kwargs)

    @extend_schema(tags=['orders'])
    def partial_update(self, request, *args, **kwargs):  # type: ignore[override]
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(tags=['orders'])
    def destroy(self, request, *args, **kwargs):  # type: ignore[override]
        return super().destroy(request, *args, **kwargs)
