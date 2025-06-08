from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='index'),
    path('',views.panel_estudiantes, name="panel_estudiantes"),
    path('estudiante/<str:id>/', views.detalle_estudiante, name='detalle_estudiante'),
    path('matricular/',views.matricular_estudiante,name='matricular_estudiante'),
    path('cancelar-curso/', views.cancelar_curso, name='cancelar_curso'),
]

    # Registro y listado
    #path('registrar/', views.registrar_estudiante, name='registrar_estudiante'),
    #ath('lista/', views.lista_estudiantes, name='lista_estudiantes'),

    # Detalle por ID
    #path('estudiante/<int:id>/', views.detalle_estudiante, name='detalle_estudiante'),

    # Agregar nota a un estudiante
    #path('estudiante/<int:id>/agregar-nota/', views.agregar_nota, name='agregar_nota'),

    # Promedios
    #path('promedios/', views.ver_promedios, name='ver_promedios'),

