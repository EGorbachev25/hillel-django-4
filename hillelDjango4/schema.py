import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLResolveInfo, GraphQLError

from orders.models import Order, OrderProduct
from products.models import Product


class ProductObjectType(DjangoObjectType):
    class Meta:
        model = Product
        filter_fields = ('id', 'name', 'price')
        interfaces = (graphene.relay.Node,)

    decoded_id = graphene.ID()

    def resolve_decoded_id(self, info):
        return self.id


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

        return queryset


class CreateOrderProductInput(graphene.InputObjectType):
    product_id = graphene.ID()
    quantity = graphene.Decimal()


class CreateOrder(graphene.Mutation):
    class Arguments:
        order_products = graphene.List(CreateOrderProductInput)

    order = graphene.Field(OrderObjectType)

    def mutate(self, info, order_products):
        user = info.context.user

        if not user.is_authenticated:
            raise GraphQLError('You must be authenticated to create an order')

        # Good way (only 2 SQL queries)
        products = Product.objects.in_bulk([op.product_id for op in order_products])
        # Verify all products exist
        if len(products) != len(order_products):
            raise GraphQLError('Some products do not exist')

        order = Order.objects.create(user=info.context.user)

        order_products_instances = [
            OrderProduct(
                order=order,
                product=products[int(op.product_id)],
                quantity=op.quantity,
                price=products[int(op.product_id)].price * op.quantity,
            )
            for op in order_products
        ]

        OrderProduct.objects.bulk_create(order_products_instances)
        order.update_total_price()

        # Bad way (SQL queries in a loop)
        # for order_product in order_products:
        #     product = Product.objects.get(pk=order_product.product_id)
        #     OrderProduct.objects.create(
        #         order=order,
        #         product=product,
        #         quantity=order_product.quantity,
        #     )

        order = Order.objects.prefetch_related('order_products__product').get(pk=order.pk)

        return CreateOrder(order=order)


class Mutation(graphene.ObjectType):
    create_order = CreateOrder.Field()


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
)
