"""point_experts_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from RoomMate_api.views import bootstrap
from RoomMate_api.views import users
from RoomMate_api.views import auth
from RoomMate_api.views import propiedad
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #Version
        path('bootstrap/version', bootstrap.VersionView.as_view()),
    #Crear Cliente/Usuario
        path('usuarios/', users.ClienteView.as_view()),
    #Editar Cliente/Usuario
        path('usuarios-edit/',users.ClienteViewEdit.as_view()),
    #Login
        path('token/', auth.CustomAuthToken.as_view()),
    #Logout
        path('logout/', auth.Logout.as_view()),
    #Create Materias
        path('propiedades/', propiedad.PropiedadesView.as_view()),   
    #Maestro Data
        path('lista-propiedades/', propiedad.PropiedadesAll.as_view()),
    #Edit Materia
        path('propiedades-edit/', propiedad.PropiedadViewEdit.as_view()),

        path('propiedades/<int:id>/', propiedad.PropiedadDetailView.as_view(), name='propiedad-detail'),

        path('propiedades/<int:propiedad_id>/comentarios/', propiedad.AgregarComentarioAPIView.as_view(), name='agregar-comentario'),


]

if settings.DEBUG:  # Solo para desarrollo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)