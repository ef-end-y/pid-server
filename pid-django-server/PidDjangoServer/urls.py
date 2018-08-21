from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload_bbl', views.upload_bbl, name='upload_bbl'),
    path('result', views.result, name='result'),
    path('download/<str:job_id>/<str:file>', views.download, name='download'),
]
