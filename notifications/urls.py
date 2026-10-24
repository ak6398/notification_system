from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_matrix_view, name='admin_matrix'),
    path('api/template/<int:template_id>/toggle/', views.toggle_template_api, name='toggle_template'),
    path('api/template/<int:template_id>/save/', views.save_template_api, name='save_template'),
    path('api/template/<int:template_id>/test-send/', views.test_send_api, name='test_send'),
    path('trigger/<slug:slug>/fire/', views.fire_manual_trigger, name='fire_manual_trigger'),
]
