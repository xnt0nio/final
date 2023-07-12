import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, permission_required
from .serializers import *
from rest_framework import viewsets
import requests
from django.contrib.auth import authenticate, login
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import Group
from datetime import datetime
from django.shortcuts import redirect, get_object_or_404
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from django.templatetags.static import static
import os
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist



def grupo_requerido(nombre_grupo):
    def decorator(view_fuc):
        @user_passes_test(lambda user: user.groups.filter(name=nombre_grupo).exists())
        def wrapper(request, *arg, **kwargs):
            return view_fuc(request, *arg, **kwargs)
        return wrapper
    return decorator



class ProductoViewsets(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    #queryset = Producto.objects.filter()

    serializer_class = ProductoSerializer

class TipoProductoViewsets(viewsets.ModelViewSet):
    queryset = TipoProducto.objects.all()
    #queryset = Producto.objects.filter()

    serializer_class = TipoProductoSerializer


class TipoSubViewsets(viewsets.ModelViewSet):
    queryset = Suscripcion.objects.all()
    #queryset = Producto.objects.filter()

    serializer_class = TipoSubSerializer


class TipoHistorialViewsets(viewsets.ModelViewSet):
    queryset = HistorialCompra.objects.all()
    #queryset = Producto.objects.filter()

    serializer_class = TipoHistorialSerializer   
####


def index(request):
    productosAll = Producto.objects.all()[:4]  # Obtener los primeros 4 productos

    data = {
        'listaProductos': productosAll
    }
    return render(request, 'core/index.html', data)

from googletrans import Translator

def indexapi(request):
    # Obtiene los datos del API
    respuesta = requests.get('http://127.0.0.1:8000/api/productos/')
    respuesta2 = requests.get('https://mindicador.cl/api')
    respuesta3 = requests.get('https://rickandmortyapi.com/api/character')
    respuesta4 = requests.get('https://api.chucknorris.io/jokes/random')

    if respuesta4.status_code == 200:
        # Obtiene el chiste en inglés
        chiste_en = respuesta4.json()["value"]

        translator = Translator()
        chiste_es = translator.translate(chiste_en, dest='es').text
    else:
        chiste_es = 'No se pudo obtener el chiste de Chuck Norris'
    productos = respuesta.json()
    monedas = respuesta2.json()
    envolvente = respuesta3.json()
    personajes = envolvente['results']
    data = {
        'listaProductos': productos,
        'monedas': monedas,
        'personajes': personajes,
        'chiste': chiste_es,
    }
    return render(request, 'core/indexapi.html', data)

# CRUD
@grupo_requerido('vendedor')
def add(request):
    data = {
        'form' : ProductoForm()
    }

    if request.method == 'POST':
        formulario = ProductoForm(request.POST, files=request.FILES) # OBTIENE LA DATA DEL FORMULARIO
        if formulario.is_valid():
            formulario.save() # INSERT INTO.....
            #data['msj'] = "Producto guardado correctamente"
            messages.success(request, "Producto almacenado correctamente")
    return render(request, 'core/add-product.html', data)

@grupo_requerido('vendedor')
def update(request, id):
    producto = Producto.objects.get(id=id) # OBTIENE UN PRODUCTO POR EL ID
    data = {
        'form' : ProductoForm(instance=producto) # CARGAMOS EL PRODUCTO EN EL FORMULARIO
    }

    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, instance=producto, files=request.FILES) # NUEVA INFORMACION
        if formulario.is_valid():
            formulario.save() # INSERT INTO.....
            #data['msj'] = "Producto actualizado correctamente"
            messages.success(request, "Producto modificado correctamente")
            data['form'] = formulario # CARGA LA NUEVA INFOR EN EL FORMULARIO

    return render(request, 'core/update-product.html', data)


@grupo_requerido('vendedor')
def delete(request, id):
    producto = Producto.objects.get(id=id) # OBTIENE UN PRODUCTO POR EL ID
    producto.delete()

    return redirect(to="index")

def about(request):
    return render(request, 'core/about.html')

def blog(request):
    return render(request, 'core/blog.html')






@grupo_requerido('cliente')
def vaciar_carrito(request):
    productos_carrito = Carrito.objects.filter(usuario=request.user)
    productos_carrito.delete()

    return redirect('confirma')  # Redireccionar a la página de inicio después de vaciar el carrito
 


import random
@grupo_requerido('cliente')
def checkout(request):
    if request.method == 'POST':
        carrito = Carrito.objects.filter(usuario=request.user)
        respuesta2 = requests.get('https://mindicador.cl/api/dolar').json()
        valor_usd = respuesta2['serie'][0]['valor']
        total_precio = Decimal(str(sum(item.producto.precio * item.cantidad_agregada for item in carrito)))
        total_en_dolar = round(total_precio / Decimal(str(valor_usd)), 2)

        # Definir valores predeterminados para descuento y total_dolares
        descuento = Decimal('0.0')
        total_con_descuento = total_precio
        total_dolares = Decimal('0.0')
        iva = round(total_precio * Decimal('0.19'))    
        total_iva = round(total_precio + iva)
        total_envio = round(total_iva + 5000)  

        # Verificar si el usuario está suscrito
        if hasattr(request.user, 'suscripcion'):
            descuento_porcentaje = Decimal('0.1')
            descuento = round(total_precio * descuento_porcentaje)
            total_con_descuento = round(total_iva - descuento)
            total_dolares = round(total_con_descuento / Decimal(str(valor_usd)), 2)

        total = total_dolares or total_en_dolar

        fecha_entrega = datetime.now().date() + timedelta(days=5)
        fecha_compra = datetime.today()

        # Generar un solo número aleatorio de pedido para el usuario actual
        numero_pedido = str(random.randint(1000, 9999))

        # Crear una lista para almacenar los objetos de HistorialCompra y Pedidos
        historiales = []
        pedidos = []

        for item in carrito:
            item.total_producto = item.producto.precio * item.cantidad_agregada
            item.save()  

            historial = HistorialCompra(
                usuario=request.user,
                producto=item.producto,
                cantidad=item.cantidad_agregada,
                fecha_compra=fecha_compra
            )
            historiales.append(historial)

            pedido = Pedido(
                usuario=request.user,
                producto=item.producto,
                cantidad=item.cantidad_agregada,
                nombre_completo=request.POST.get('nombre_completo'),
                region=request.POST.get('region'),
                comuna=request.POST.get('comuna'),
                direccion=request.POST.get('direccion'),
                nro_casa_departamento=request.POST.get('nro_casa_departamento'),
                celular=request.POST.get('celular'),
                correo=request.POST.get('correo'),
                comentario=request.POST.get('comentario'),
                fecha_entrega=fecha_entrega,
                numero_pedido=numero_pedido
            )
            pedidos.append(pedido)

            BoletaCompra.objects.create(
                usuario=request.user,
                producto=item.producto,
                cantidad=item.cantidad_agregada,
                fecha_compra=timezone.now(),
                precio_unitario=item.producto.precio,              
                precio_total=total_precio,
                monto_neto=total_con_descuento,
                iva=iva,
                descuento=descuento
            )

        # Crear los registros de historial de compra en una sola operación
        HistorialCompra.objects.bulk_create(historiales)

        # Crear los registros de pedidos en una sola operación
        Pedido.objects.bulk_create(pedidos)

        datos = {
            'listarproductos': carrito,
            'total_precio': total_precio,
            'total_envio': total_envio,
            'descuento': descuento,
            'total_con_descuento': total_con_descuento,
            'total_dolares': total_dolares,
            'total_en_dolar': total_en_dolar,
            'total': total,
            'iva': iva,
            'total_iva': total_iva,
            'suscrito': hasattr(request.user, 'suscripcion')
        }
        return render(request, 'core/checkout.html', datos)

    else:
        # Código para la solicitud GET (cuando se carga la página)
        carrito = Carrito.objects.filter(usuario=request.user)
        total_precio = Decimal('0')

        for item in carrito:
            item.total_producto = item.producto.precio * item.cantidad_agregada
            total_precio += item.total_producto

        iva = round(total_precio * Decimal('0.19'))    
        total_iva = total_precio + iva
        total_envio = total_iva + 5000      

        respuesta2 = requests.get('https://mindicador.cl/api/dolar').json()
        valor_usd = respuesta2['serie'][0]['valor']
        total_en_dolar = round(total_envio / Decimal(str(valor_usd)), 2)

        descuento = Decimal('0.0')
        total_con_descuento = total_envio
        total_dolares = Decimal('0.0')

        if hasattr(request.user, 'suscripcion'):
            descuento_porcentaje = Decimal('0.1')
            descuento = round(total_precio * descuento_porcentaje)
            total_con_descuento = round(total_iva - descuento)
            total_dolares = round(total_con_descuento / Decimal(str(valor_usd)), 2)

        total = total_dolares or total_en_dolar

        datos = {
            'listarproductos': carrito,
            'total_precio': total_precio,
            'total_envio': total_envio,
            'descuento': descuento,
            'total_con_descuento': total_con_descuento,
            'total_dolares': total_dolares,
            'total_en_dolar': total_en_dolar,
            'total': total,
            'iva': iva,
            'total_iva': total_iva,
            'suscrito': hasattr(request.user, 'suscripcion')
        }
        return render(request, 'core/checkout.html', datos)




def crear(request):
    return render(request, 'core/crear.html')


def pagosub(request):
    return render(request, 'core/pagosub.html')

def contact(request):
    return render(request, 'core/contact.html')



def shopgrid(request):
    categorias = TipoProducto.objects.all()  # Obtén todos los tipos de productos (categorías)
    categoria_seleccionada = request.GET.get('categoria')  # Obtiene la categoría seleccionada de la URL

    if categoria_seleccionada:  # Si se seleccionó una categoría
        productosAll = Producto.objects.filter(tipo__descripcion=categoria_seleccionada)
    else:
        productosAll = Producto.objects.all()

    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(productosAll, 5)
        productosAll = paginator.page(page)
    except:
        raise Http404

    data = {
        'listado': productosAll,
        'paginator': paginator,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada
    }
    return render(request, 'core/shop-grid.html', data)




@grupo_requerido('cliente')
def shopdetails(request, id):
    producto = Producto.objects.get(id=id)

    if request.method == 'POST':
        cantidad_agregada = int(request.POST.get('cantidad_agregada', 1))

        # Verificar si hay suficiente stock disponible
        if producto.stock >= cantidad_agregada:
            # Obtener el carrito del usuario actual
            carrito, created = Carrito.objects.get_or_create(usuario=request.user, producto=producto)

            # Actualizar la cantidad agregada en el carrito
            carrito.cantidad_agregada += cantidad_agregada
            carrito.save()

            # Restar la cantidad del carrito al stock del producto
            producto.stock -= cantidad_agregada
            producto.save()
        
            messages.success(request, "Producto almacenado correctamente")
        else:
            messages.error(request, "No hay suficiente stock disponible")

    data = {'Productos': producto}
    return render(request, 'core/shop-details.html', data)
  

def main(request):
    return render(request, 'core/main.html')


#carrito
# shoping es donde se almacena cuando aniadimos al carrito 
@grupo_requerido('cliente')
def shopingcart(request):
    carrito = Carrito.objects.filter(usuario=request.user)
    total_precio = 0

    for item in carrito:
        item.total_producto = item.producto.precio * item.cantidad_agregada
        total_precio += item.total_producto

    descuento = Decimal('0.0')
    total_con_descuento = total_precio
    if hasattr(request.user, 'suscripcion'):
            descuento_porcentaje = Decimal('0.1')
            descuento = round(total_precio * descuento_porcentaje)
            total_con_descuento = round(total_precio - descuento)    

    datos = {
        'listarproductos': carrito,
        'total_precio': total_precio,
        'descuento': descuento,
        'total_con_descuento': total_con_descuento,
        'suscrito': hasattr(request.user, 'suscripcion')
    }

    return render(request, 'core/shoping-cart.html', datos)


@grupo_requerido('cliente')
def eliminar_producto(request, id):
    carro = Carrito.objects.get(id=id)
    producto = carro.producto

    # Sumar la cantidad del carrito al stock del producto
    producto.stock += carro.cantidad_agregada
    producto.save()

    carro.delete()
    return redirect("shopingcart")
    


def registro(request):
    data = {
        'form': CustomUserCreationForm()
    }
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            user = authenticate(username=formulario.cleaned_data["username"], password=formulario.cleaned_data["password1"])
            grupo = Group.objects.get(name="cliente")
            user.groups.add(grupo)
            login(request, user)
            messages.success(request, "Te has registrado correctamente")
            #redirigir al home
            return redirect(to="index")
        data["form"] = formulario    
    return render(request, 'registration/registro.html',data)


@grupo_requerido('cliente')
def suscripcion(request):
    user = request.user
    suscripcion = Suscripcion.objects.filter(usuario=user).first()

    if suscripcion:
        suscrito = True
        fecha_inicio = suscripcion.fecha_inicio.strftime('%m/%d')
        fecha_termino = suscripcion.fecha_finalizacion.strftime('%m/%d')
    else:
        suscrito = False
        fecha_inicio = None
        fecha_termino = None

    if request.method == 'POST':
        form = SuscripcionForm(request.POST)
        if form.is_valid():
            suscripcion = form.save(commit=False)
            suscripcion.usuario = user
            suscripcion.fecha_inicio = timezone.now()
            suscripcion.fecha_finalizacion = suscripcion.fecha_inicio + timedelta(days=30)
            suscripcion.save()

            messages.success(request, '¡Te has suscrito correctamente!')
            return redirect('index')
    else:
        form = SuscripcionForm()

    return render(request, 'core/suscripcion.html', {'form': form, 'suscrito': suscrito, 'fecha_inicio': fecha_inicio, 'fecha_termino': fecha_termino})

@grupo_requerido('cliente')
def cancelar_suscripcion(request):
    suscripcion = Suscripcion.objects.get(usuario=request.user)
    suscripcion.delete()
    messages.success(request, '¡Tu suscripción ha sido cancelada correctamente!')
    return redirect('index')

 # Requiere que el usuario esté autenticado
@grupo_requerido('cliente')
def seguimiento(request):
    if request.user.is_superuser:  # Verifica si el usuario es un administrador
        pedidos = Pedido.objects.all()  # Obtiene todos los pedidos
    else:
        pedidos = Pedido.objects.filter(usuario=request.user)  # Filtra los pedidos del usuario actual

    return render(request, 'core/seguimiento.html', {'pedidos': pedidos})

@grupo_requerido('cliente')
def historial(request):
    historial_compras = HistorialCompra.objects.filter(usuario=request.user)

    for compra in historial_compras:
        compra.total_productos = compra.producto.precio * compra.cantidad

    page_number = request.GET.get('page',1)

    paginator = Paginator(historial_compras, 6)  # Mostrar 10 elementos por página
    page_obj = paginator.page(page_number)

    datos = {
        'historial_compras': page_obj
    }
    return render(request, 'core/historial.html', datos)


@grupo_requerido('vendedor')
def cambiar_estado_pedido(request, pedido_id):
    # Obtener el pedido específico
    pedido = Pedido.objects.get(pk=pedido_id)

    if request.method == 'POST':
        # Obtener el nuevo estado seleccionado
        nuevo_estado = request.POST.get('nuevo_estado')

        # Actualizar el estado del pedido
        pedido.estado = nuevo_estado
        pedido.save()
        return redirect('seguimiento')
    return render(request, 'core/seguimiento.html', {'pedido': pedido})




@grupo_requerido('cliente')
def confirma(request):
    boletas = BoletaCompra.objects.filter(usuario=request.user)
    
    try:
        suscripcion = Suscripcion.objects.get(usuario=request.user)
    except ObjectDoesNotExist:
        suscripcion = None
    
    datos = {
        'boletas': boletas,
        'suscripcion': suscripcion
    }
    
    return render(request, 'core/confirma.html', datos)










@grupo_requerido('cliente')
def descargar_pdf(request):
    boletas = BoletaCompra.objects.filter(usuario=request.user)

    try:
        suscripcion = Suscripcion.objects.get(usuario=request.user)
    except Suscripcion.DoesNotExist:
        suscripcion = None

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="voucher.pdf"'

    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []

    # Estilos de fuente y formato
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']

    # Título
    title = Paragraph("Boletas:", title_style)
    story.append(title)
    story.append(Spacer(1, 12))  # Espaciado después del título

    # Tabla de boletas
    data = [['#', 'Nombre', 'Fecha compra', 'Cantidad', 'Precio unitario']]
    for i, boleta in enumerate(boletas):
        data.append([str(i+1), boleta.producto.nombre, boleta.fecha_compra.strftime('%d de %B de %Y a las %H:%M'), str(boleta.cantidad), str(boleta.precio_unitario)])

    table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), '#7fad39'),
                              ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
                              ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                              ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                              ('FONTSIZE', (0, 0), (-1, 0), 12),
                              ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                              ('BACKGROUND', (0, 1), (-1, -1), 'white'),
                              ('FONTSIZE', (0, 1), (-1, -1), 10),
                              ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                              ('GRID', (0, 0), (-1, -1), 1, '#bfbfbf')])

    table = Table(data, style=table_style)
    story.append(table)
    story.append(Spacer(1, 24))  # Espaciado después de la tabla

    # Resumen
    subtitle = Paragraph("Resumen:", subtitle_style)
    story.append(subtitle)

    summary = []
    summary.append(Paragraph(f"SubTotal: {boletas[0].precio_total}", normal_style))
    summary.append(Paragraph(f"IVA (19%): {boletas[0].iva}", normal_style))
    if suscripcion:
        summary.append(Paragraph(f"Descuento: {boletas[0].descuento}", normal_style))

    summary.append(Paragraph(f"Total: {boletas[0].monto_neto}", normal_style))  # Agregar el total
    summary.append(Spacer(1, 12))  # Espaciado después del total

    # Agregar el rut de la empresa
    summary.append(Paragraph("Rut de la empresa: 12.345.678-9", normal_style))

    story.append(Table([summary]))

    story.append(Spacer(1, 24))  # Espaciado después del resumen

    # Agregar imagen
    ruta_imagen = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'core', 'img', 'images.jpg') # Ruta de tu imagen
    imagen = Image(ruta_imagen, width=200, height=200)  # Ajusta el ancho y alto según tus necesidades
    story.append(imagen)
    story.append(Spacer(1, 24))  # Espaciado después de la imagen

    # Generar el PDF
    doc.build(story)

    return response


@grupo_requerido('cliente')
def borrar_datos(request):
    boletas = BoletaCompra.objects.filter(usuario=request.user)
    boletas.delete()  # Elimina las boletas asociadas al usuario

    return redirect('seguimiento')

@grupo_requerido('cliente')
def borrar_datos2(request):
    boleta = BoletaCompra.objects.filter(usuario=request.user)
    boleta.delete()  # Elimina las boletas asociadas al usuario

    return redirect('historial')



@grupo_requerido('cliente')
def borrar_datos3(request):
    bolet = BoletaCompra.objects.filter(usuario=request.user)
    bolet.delete()  # Elimina las boletas asociadas al usuario

    return redirect('index')