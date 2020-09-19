from django.views.generic import DetailView, CreateView, UpdateView, DeleteView 
from django.urls import reverse, reverse_lazy

from .base_views import SearchView

from webapp.models import Product
from webapp.forms import ProductForm


class IndexView(SearchView):
    model = Product
    template_name = 'product/index.html'
    ordering = ['category', 'name']
    search_fields = ['name__icontains']
    paginate_by = 5
    context_object_name = 'products'

    def dispatch(self, request, *args, **kwargs):
        self.test_session_key()
        self.test_session_data()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(amount__gt=0)

    def test_session_key(self):
        print(self.request.session.session_key)
        if not self.request.session.session_key:
            self.request.session.save()

    def test_session_data(self):
        if 'check' not in self.request.session:
            self.request.session['check'] = 0
        self.request.session['check'] += 1
        print(self.request.session['check'])


class ProductView(DetailView):
    model = Product
    template_name = 'product/product_view.html'

    # чтоб товары, которых не осталось нельзя было и просмотреть
    # это можно добавить вместо model = Product в Detail, Update и Delete View.
    # def get_queryset(self):
    #     return super().get_queryset().filter(amount__gt=0)


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_create.html'

    def get_success_url(self):
        return reverse('webapp:product_view', kwargs={'pk': self.object.pk})


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_update.html'

    def get_success_url(self):
        return reverse('webapp:product_view', kwargs={'pk': self.object.pk})


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product/product_delete.html'
    success_url = reverse_lazy('webapp:index')
