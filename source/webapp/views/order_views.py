from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView

from webapp.forms import CartAddForm, OrderForm
from webapp.models import Cart, Product, Order, OrderProduct


class CartView(ListView):
    # model = Cart
    template_name = 'order/cart_view.html'
    context_object_name = 'cart'

    # вместо model = Cart
    # для выполнения запроса в базу через модель
    # вместо подсчёта total-ов в Python-е.
    def get_queryset(self):
        return Cart.get_with_product().filter(pk__in=self.get_cart_ids())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['cart_total'] = Cart.get_cart_total(ids=self.get_cart_ids())
        context['form'] = OrderForm()
        return context

    def get_cart_ids(self):
        cart_ids = self.request.session.get('cart_ids', [])
        print(cart_ids)
        return self.request.session.get('cart_ids', [])


class CartAddView(CreateView):
    model = Cart
    form_class = CartAddForm

    def post(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=self.kwargs.get('pk'))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # qty = 1
        # бонус
        qty = form.cleaned_data.get('qty', 1)

        try:
            cart_product = Cart.objects.get(product=self.product, pk__in=self.get_cart_ids())
            cart_product.qty += qty
            if cart_product.qty <= self.product.amount:
                cart_product.save()
        except Cart.DoesNotExist:
            if qty <= self.product.amount:
                cart_product = Cart.objects.create(product=self.product, qty=qty)
                self.save_to_session(cart_product)

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        return redirect(self.get_success_url())

    def get_success_url(self):
        # бонус
        next = self.request.GET.get('next')
        if next:
            return next
        return reverse('webapp:index')

    def get_cart_ids(self):
        return self.request.session.get('cart_ids', [])

    def save_to_session(self, cart_product):
        cart_ids = self.request.session.get('cart_ids', [])
        if cart_product.pk not in cart_ids:
            cart_ids.append(cart_product.pk)
        self.request.session['cart_ids'] = cart_ids


class CartDeleteView(DeleteView):
    model = Cart
    success_url = reverse_lazy('webapp:cart_view')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.delete_from_session()
        self.object.delete()
        return redirect(success_url)

    def delete_from_session(self):
        cart_ids = self.request.session.get('cart_ids', [])
        cart_ids.remove(self.object.pk)
        self.request.session['cart_ids'] = cart_ids

    # удаление без подтверждения
    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


# бонус
class CartDeleteOneView(CartDeleteView):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        self.object.qty -= 1
        if self.object.qty < 1:
            self.delete_from_session()
            self.object.delete()
        else:
            self.object.save()

        return redirect(success_url)


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('webapp:index')

    # def form_valid(self, form):
    #     response = super().form_valid(form)
    #     order = self.object
    #     # неоптимально: на каждый товар в корзине идёт 3 запроса:
    #     # * добавить товар в заказ
    #     # * обновить остаток товара
    #     # * удалить товар из корзины
    #     for item in Cart.objects.all():
    #         product = item.product
    #         qty = item.qty
    #         order.order_products.create(product=product, qty=qty)
    #         product.amount -= qty
    #         product.save()
    #         item.delete()
    #     return response

    def form_valid(self, form):
        response = super().form_valid(form)
        order = self.object
        # оптимально:
        # цикл сам ничего не создаёт, не обновляет, не удаляет
        # цикл работает только с объектами в памяти
        # и заполняет два списка: products и order_products
        cart_products = Cart.objects.all()
        products = []
        order_products = []
        for item in cart_products:
            product = item.product
            qty = item.qty
            product.amount -= qty
            products.append(product)
            order_product = OrderProduct(order=order, product=product, qty=qty)
            order_products.append(order_product)
        # массовое создание всех товаров в заказе
        OrderProduct.objects.bulk_create(order_products)
        # массовое обновление остатка у всех товаров
        Product.objects.bulk_update(products, ('amount',))
        # массовое удаление всех товаров в корзине
        cart_products.delete()
        return response

    def form_invalid(self, form):
        return redirect('webapp:cart_view')
