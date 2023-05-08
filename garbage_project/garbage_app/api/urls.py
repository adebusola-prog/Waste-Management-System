from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns=[
   # path('api/posts', views.PostList.as_view(), name='post_list'),
   # path('api/<int:pk>/post', views.PostDetail.as_view(), name='post_detail'),
   # path('api/categories', views.CategoryList.as_view(), name='category_list'),
   # path('api/<int:pk>/category', views.CategoryDetail.as_view(), name='category_detail'),
   # path('api/comments', views.CommentList.as_view(), name='comment_list'),
   # path('api/<int:pk>/comment', views.CommentDestroy.as_view(), name='comment_delete'),


]
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])