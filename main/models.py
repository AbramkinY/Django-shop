from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Название категории') #символы
    slug = models.SlugField(unique=True)                                                #ссылки
    img = models.ImageField(verbose_name='Изображение', null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})


class Product(models.Model):

    title = models.CharField(max_length=255, verbose_name='Название продукта')
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание')
    qty = models.PositiveIntegerField(default=0, verbose_name='Количество')

    def get_model_name(self):
        return self.__class__.__name__.lower()    #обращение к классу нижнего регистра

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})               #ссылка на обьект класса продукт


class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)   #при удалении записи в табл будут удалены и те, на которые ссылаються
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')
    product_in_order = models.ForeignKey('Order', on_delete=models.CASCADE, verbose_name='Заказ', null=True)

    def __str__(self):
        return "Продукт: {} для корзины".format(self.product.title)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.product.price
        super().save(*args, **kwargs)                                                 #сумма продуктов в корзине,


class Cart(models.Model):

    owner = models.ForeignKey('Customer', null=True, verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    address = models.CharField(max_length=255, verbose_name='Адресс', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_customer')
    phone = models.CharField(max_length=255, verbose_name='Номер телефона', null=True, blank=True)

    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)


class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='related_orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name='Статус заказ',
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Тип заказа',
        choices=BUYING_TYPE_CHOICES,
        null = True
    )
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now, null=True)

    def str(self):
        return str(self.id)