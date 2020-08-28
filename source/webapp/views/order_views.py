from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView

from webapp.forms import CartAddForm
from webapp.models import Cart, Product


class CartView(ListView):
    model = Cart
    template_name = 'order/cart_view.html'
    context_object_name = 'cart'

    # вместо model = Cart
    # для выполнения запроса в базу через модель
    # вместо подсчёта total-ов в Python-е.
    # def get_queryset(self):
    #     return Cart.get_with_total()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['cart_total'] = Cart.get_cart_total()
        return context


class CartAddView(CreateView):
    model = Cart
    form_class = CartAddForm

    def post(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=self.kwargs.get('pk'))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        qty = 1
        # бонус
        # qty = form.cleaned_data.get('qty', 1)

        try:
            cart_product = Cart.objects.get(product=self.product)
            cart_product.qty += qty
            if cart_product.qty <= self.product.amount:
                cart_product.save()
        except Cart.DoesNotExist:
            if qty <= self.product.amount:
                Cart.objects.create(product=self.product, qty=qty)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        # бонус
        # next = self.request.GET.get('next')
        # if next:
        #     return next
        return reverse('index')


class CartDeleteView(DeleteView):
    model = Cart
    success_url = reverse_lazy('cart_view')

    # удаление без подтверждения
    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    # бонус
    # def delete(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     success_url = self.get_success_url()
    # 
    #     self.object.qty -= 1
    #     if self.object.qty < 1:
    #         self.object.delete()
    #     else:
    #         self.object.save()
    # 
    #     return HttpResponseRedirect(success_url)
