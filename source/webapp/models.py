from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F, ExpressionWrapper as E


DEFAULT_CATEGORY = 'other'
CATEGORY_CHOICES = (
    (DEFAULT_CATEGORY, 'Разное'),
    ('food', 'Продукты питания'),
    ('household', 'Хоз. товары'),
    ('toys', 'Детские игрушки'),
    ('appliances', 'Бытовая Техника')
)


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(max_length=2000, null=True, blank=True, verbose_name='Описание')
    category = models.CharField(max_length=20, verbose_name='Категория',
                                choices=CATEGORY_CHOICES, default=DEFAULT_CATEGORY)
    amount = models.IntegerField(verbose_name='Остаток', validators=[MinValueValidator(0)])
    price = models.DecimalField(verbose_name='Цена', max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.name} - {self.amount}'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Cart(models.Model):
    product = models.ForeignKey('webapp.Product', on_delete=models.CASCADE,
                                verbose_name='Товар', related_name='in_cart')
    qty = models.IntegerField(verbose_name='Количество', default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.product.name} - {self.qty}'

    # def get_total(self):
    #     return self.qty * self.product.price

    @classmethod
    def get_with_total(cls):
        # запрос, так быстрее
        total_output_field = models.DecimalField(max_digits=10, decimal_places=2)
        total_expr = E(F('qty') * F('product__price'), output_field=total_output_field)
        return cls.objects.annotate(total=total_expr)

    @classmethod
    def get_with_product(cls):
        return cls.get_with_total().select_related('product')

    # @classmethod
    # def get_cart_total(cls):
    #     total = 0
    #     for item in cls.objects.all():
    #         total += item.get_total()
    #     return total

    @classmethod
    def get_cart_total(cls, ids=None):
        # запрос, так быстрее
        cart_products = cls.get_with_total()
        if ids is not None:
            cart_products = cart_products.filter(pk__in=ids)
        total = cart_products.aggregate(cart_total=Sum('total'))
        return total['cart_total']

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'


class Order(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя')
    phone = models.CharField(max_length=30, verbose_name='Телефон')
    address = models.CharField(max_length=100, verbose_name='Адрес')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    products = models.ManyToManyField('webapp.Product', related_name='orders', verbose_name='Товары',
                                      through='webapp.OrderProduct', through_fields=['order', 'product'])

    def __str__(self):
        return f'{self.name} - {self.phone} - {self.format_time()}'

    def format_time(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderProduct(models.Model):
    product = models.ForeignKey('webapp.Product', on_delete=models.CASCADE,
                                verbose_name='Товар', related_name='order_products')
    order = models.ForeignKey('webapp.Order', on_delete=models.CASCADE,
                              verbose_name='Заказ', related_name='order_products')
    qty = models.IntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.product.name} - {self.order.name} - {self.order.format_time()}'

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'
