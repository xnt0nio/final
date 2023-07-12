from django import views
from django.urls import path, include
from .views import *
from rest_framework import routers

#Creamos las rutas del api
router = routers.DefaultRouter()
router.register('productos', ProductoViewsets)
router.register('tipoproductos', TipoProductoViewsets)
router.register('tipoSuscripcion', TipoSubViewsets)
router.register('historial', TipoHistorialViewsets)


urlpatterns = [
    #api
    path('api/', include(router.urls)),

    #rutas
    path('', index, name="index"),
    path('indexapi', indexapi, name="indexapi"),
    path('blog/', blog, name="blog"),
    path('shopingcart/', shopingcart, name="shopingcart"),
    path('checkout/', checkout, name="checkout"),
    path('contact/', contact, name="contact"),
    path('shopgrid/', shopgrid, name="shopgrid"),
    path('shopdetails/<id>/', shopdetails, name="shopdetails"),
    path('historial/', historial, name="historial"),
    path('crear/', crear, name="crear"), 
    path('pagosub/', pagosub, name="pagosub"),
    path('suscripcion/', suscripcion, name="suscripcion"),
    path('main/', main, name="main"),

    #CRUD
    path('add/', add, name="add"),
    path('update/<id>/', update, name="update"),
    path('delete/<id>/', delete, name="delete"),
    path('eliminar_producto/<id>/', eliminar_producto, name="eliminar_producto"),
    path('vaciar_carrito/', vaciar_carrito, name='vaciar_carrito'),
    path('cancelar_suscripcion/', cancelar_suscripcion, name='cancelar_suscripcion'),
    path('registro/', registro, name='registro'),
    path('seguimiento/', seguimiento, name='seguimiento'),
    path('cambiar_estado/<int:pedido_id>/', cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('confirma', confirma, name='confirma'),
    path('descargar_pdf/', descargar_pdf, name='descargar_pdf'),
    path('borrar_datos/', borrar_datos, name='borrar_datos'),
    path('borrar_datos2', borrar_datos2, name='borrar_datos2'),
    path('borrar_datos3', borrar_datos3, name='borrar_datos3'),
    path('accounts/', include('django.contrib.auth.urls')),

 




   


    
]