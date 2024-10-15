from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.response import Response

from orders.models import Order
from orders.serialializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        cache_key = f'orders:{user_id}'

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        data = serializer.data

        cache.set(cache_key, data, timeout=60 * 60)

        return Response(data)
