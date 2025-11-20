from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_query, name='analyze_query'),
    path('download/', views.download_data, name='download_data'),
    path('download-sample/', views.download_sample_data, name='download_sample_data')
]