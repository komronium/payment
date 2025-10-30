from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PaymeWebhookView,
    PaymeCreateLinkView,
    PaymeCreateLinkByOrderView,
    PaymeCreateLinkNewOrderView,
    OrderViewSet,
)


router = DefaultRouter()
router.register('api/orders', OrderViewSet, basename='order')

urlpatterns = [
    path('webhooks/payme/', PaymeWebhookView.as_view(), name='payme_webhook'),
    # Payme payment link endpoints (2 clear variants)
    path('api/payments/payme/links/<int:order_id>/', PaymeCreateLinkByOrderView.as_view(), name='payme_link_for_order'),
    path('api/payments/payme/links/', PaymeCreateLinkNewOrderView.as_view(), name='payme_link_new_order'),
    path('', include(router.urls)),
]


