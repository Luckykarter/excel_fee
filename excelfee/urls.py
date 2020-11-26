from django.urls import path
import excelfee.views as views

urlpatterns = [
    path("calculate_fee/", views.calculate_fee),
    path("calculate/", views.calculate),
    path('show_files/', views.show_files),
    path('<str:filename>/<str:property>', views.get_property),
    path('upload_excel/', views.upload_excel)
]
