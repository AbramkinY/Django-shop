# Generated by Django 4.0.2 on 2022-03-10 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_order_buying_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartproduct',
            name='product_in_order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='product',
            name='qty',
            field=models.PositiveIntegerField(default=0, verbose_name='Количество'),
        ),
    ]