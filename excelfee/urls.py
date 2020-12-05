from django.urls import path
import excelfee.views as views

urlpatterns = [
    path("calculate/", views.calculate),
    path('<str:id>/<str:property>', views.get_property),
    path('upload_excel/', views.upload_excel),
]
