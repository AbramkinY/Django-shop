# Generated by Django 4.0.2 on 2022-02-27 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_customer_phone_product_qty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='buying_type',
            field=models.CharField(choices=[('self', 'Самовывоз'), ('delivery', 'Доставка')], max_length=100, null=True, verbose_name='Тип заказа'),
        ),
    ]
