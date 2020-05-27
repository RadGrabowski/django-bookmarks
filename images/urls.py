from django.urls import path
from . import views

app_name = 'images'

urlpatterns = [
    path('', views.ImageListView.as_view(), name='list'),
    path('create/', views.ImageCreateView.as_view(), name='create'),
    path('detail/<pk>/<slug>', views.ImageDetailView.as_view(), name='detail'),
    path('like/', views.image_like, name='like'),
    path('ranking/', views.ImageRankingView.as_view(), name='ranking')
]