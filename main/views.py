from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView

from .forms import RegisterUserForm, AuthUserForm, OrderForm
from .mixins import CartMixin
from .models import Category, Customer, Product, CartProduct, Order
from .utils import recalc_cart


class MainView(ListView, CartMixin):

    model = Category
    template_name = 'index.html'
    categories = Category.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


class RegisterUserView(CartMixin):

    def get(self, request, *args, **kwargs):

        form = RegisterUserForm(request.POST or None)
        context = {'form': form, 'cart': self.cart}
        return render(request, 'registration.html', context)

    def post(self, request, *args, **kwargs):

        form = RegisterUserForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit= False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
            )
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/')

        context = {'form': form, 'cart': self.cart}
        return render(request, 'registration.html', context)


class ProductList(ListView, CartMixin):

    model = Product
    context_object_name = 'product_by_category'
    template_name = 'product_list.html'

    def get_queryset(self):
        return Product.objects.filter(category__slug=self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


class LoginView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        form = AuthUserForm(request.POST or None)
        context = {'form': form, 'cart': self.cart}
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = AuthUserForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {'form': form, 'cart': self.cart}
        return render(request, 'login.html', context)


class ProductDetailView(DetailView, CartMixin):

    model = Product
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, product=product
        )
        if created:
            self.cart.products.add(cart_product)
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно добавлен")
        return HttpResponseRedirect('/cart/')


class ChangeQTYView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        prod_qty = product.qty
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product
        )
        qty = int(request.POST.get('qty'))
        if qty > prod_qty:
            messages.add_message(request, messages.INFO, f"Это количество недоступно. В наличии {product.qty}")
            return HttpResponseRedirect('/cart/')
        else:
            cart_product.qty = qty
            cart_product.save()
            recalc_cart(self.cart)
            messages.add_message(request, messages.INFO, "Кол-во успешно изменено")
            return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product
            )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно удален")
        return HttpResponseRedirect('/cart/')


class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        context = {
            'cart': self.cart,
        }
        return render(request, 'cart.html', context)


class CheckoutView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'categories': categories,
            'form': form
        }
        return render(request, 'checkout.html', context)


class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        cart_product = CartProduct.objects.filter(user=self.cart.owner, cart=self.cart)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            order = Order.objects.filter(customer=customer).latest('created_at')
            for product in cart_product:
                product.product_in_order = order
                product.save()
                product.product.qty = product.product.qty - product.qty
                product.product.save()
            messages.add_message(request, messages.INFO, 'Заказ оформлен!')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout/')


class ProfileView(CartMixin, View):
    def get(self, request, *args, **kwargs):
            customer = Customer.objects.get(user=request.user)
            orders = Order.objects.filter(customer=customer).order_by('-created_at')
            return render(
                request,
                'profile.html',
                {'orders': orders, 'cart': self.cart}
            )
