import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLResolveInfo

from orders.models import Order, OrderProduct
from products.models import Product


class ProductObjectType(DjangoObjectType):
    class Meta:
        model = Product
        filter_fields = ('id', 'name', 'price')
        interfaces = (graphene.relay.Node,)


class OrderProductObjectType(DjangoObjectType):
    product = graphene.Field(ProductObjectType)

    class Meta:
        model = OrderProduct
        filter_fields = ('product', 'quantity', 'price')


class OrderObjectType(DjangoObjectType):
    order_products = graphene.List(OrderProductObjectType)

    def resolve_order_products(self, info):
        return self.order_products.all()

    class Meta:
        model = Order
        fields = ('uuid', 'user', 'total_price', 'created_at', 'updated_at', 'order_products')


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi!")

    products = DjangoFilterConnectionField(ProductObjectType)
    orders = graphene.List(OrderObjectType)

    def resolve_orders(self, info: GraphQLResolveInfo):
        # return Order.objects.all().prefetch_related('order_products__product')

        queryset = Order.objects.all()

        # If selected order products, prefetch them
        fields = info.field_nodes[0].selection_set.selections

        for field in fields:
            if field.name.value == 'orderProducts':
                queryset = queryset.prefetch_related('order_products')

                # Check for nested fields
                nested_fields = field.selection_set.selections

                for nested_field in nested_fields:
                    if nested_field.name.value == 'product':
                        queryset = queryset.prefetch_related('order_products__product')
                        break

                break

        print("=" * 20)
        return queryset


schema = graphene.Schema(query=Query)
