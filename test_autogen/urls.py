from django.urls import path
import test_autogen.views as views

urlpatterns = [
    path('inflid/', views.get_contract),
]