# Generated by Django 3.1.2 on 2023-06-27 21:01

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Suscripcion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateTimeField(auto_now_add=True)),
                ('fecha_finalizacion', models.DateTimeField(blank=True, null=True)),
                ('activa', models.BooleanField(default=True)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('precio', models.IntegerField()),
                ('stock', models.IntegerField()),
                ('descripcion', models.CharField(max_length=250)),
                ('vencimiento', models.DateField(default=datetime.date.today)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='')),
                ('vigente', models.BooleanField()),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.tipoproducto')),
            ],
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_entrega', models.DateField(null=True)),
                ('nombre_completo', models.CharField(blank=True, max_length=100)),
                ('cantidad', models.IntegerField(default=0, null=True)),
                ('region', models.CharField(blank=True, max_length=100)),
                ('comuna', models.CharField(blank=True, max_length=100)),
                ('direccion', models.CharField(blank=True, max_length=200)),
                ('nro_casa_departamento', models.CharField(blank=True, max_length=50)),
                ('celular', models.CharField(blank=True, max_length=100)),
                ('correo', models.CharField(blank=True, max_length=100)),
                ('comentario', models.TextField(blank=True)),
                ('estado', models.CharField(choices=[('validacion', 'Validación'), ('preparacion', 'Preparación'), ('reparto', 'Reparto'), ('entregado', 'Entregado')], default='validacion', max_length=50)),
                ('numero_pedido', models.CharField(default='1', max_length=50, unique=True)),
                ('producto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.producto')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HistorialCompra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField(default=0)),
                ('fecha_compra', models.DateTimeField(auto_now_add=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Carrito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_agregada', models.IntegerField(default=0)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.producto')),
                ('usuario', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'db_carrito',
            },
        ),
        migrations.CreateModel(
            name='BoletaCompra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('fecha_compra', models.DateTimeField(auto_now_add=True)),
                ('precio_unitario', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('precio_total', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('monto_neto', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('iva', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('descuento', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
