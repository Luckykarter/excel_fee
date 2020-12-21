from django.urls import path
import excelfee.views as views

urlpatterns = [
    path("calculate/cells/", views.calculate_cells),
    path("calculate/file/", views.calculate_file),
    path('<str:id>/<str:property>', views.get_property),
    path('upload_excel/', views.upload_excel),
    # path('download/', views.download)
]
