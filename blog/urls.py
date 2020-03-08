from django.urls import path

from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
)

urlpatterns = [
    path('', PostListView.as_view(), name='news'),
    path('<int:pk>', PostDetailView.as_view(), name='post-detail'),
    path('new/', PostCreateView.as_view(), name='post-create'),
    path('update/<int:pk>/', PostUpdateView.as_view(), name='post-update'),
    path('delete/<int:pk>', PostDeleteView.as_view(), name='post-delete')

]
