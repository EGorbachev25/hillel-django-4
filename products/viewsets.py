from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from products.filtersets import ProductFilterSet
from products.models import Product
from products.serializers import ProductSerializer
from datetime import datetime


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('category').prefetch_related('tags')
    serializer_class = ProductSerializer
    # GET, POST, PUT, PATCH, DELETE

    authentication_classes = []
    permission_classes = []
    filterset_class = ProductFilterSet
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'price']
    ordering_fields = ['name', 'price', 'id']

    @action(detail=False, methods=['get'])
    def popular(self, request):
        # popular_products = Product.objects.raw(
        #     "select * from products_product limit 10"
        # )
        #
        # return Response(self.serializer_class(popular_products, many=True).data)

        # Get from cache
        start = datetime.now()
        cached_data = cache.get('popular_products')
        end = datetime.now()
        if cached_data:
            print(f'Cache execution time: {(end - start).total_seconds()} seconds')
            return Response(cached_data)

        start = datetime.now()
        queryset = self.get_queryset().popular()[:10]
        end = datetime.now()

        print(f'Execution time: {(end - start).total_seconds()} seconds')

        data = self.serializer_class(queryset, many=True).data

        # Store in cache
        cache.set('popular_products', data, timeout=60 * 60)

        return Response(self.serializer_class(queryset, many=True).data)
