from django.urls import path
from django.contrib.auth import views as auth_views

from . import views



app_name='accounts'

urlpatterns=[
   path("sign_up/", views.sign_up, name="sign_up"),
   path("customer_sign_up/", views.customer_sign_up, name="customer_sign_up"),
   path("sign_in/", views.user_sign_in, name="sign_in"),
   path("customer_sign_in/", views.customer_sign_in, name="customer_sign_in"),
   path("sign_out/", views.user_sign_out, name="sign_out"),
   path("password_recovery/", views.recover_password, name="recover_password"),
   path("profile/<int:pk>/update_details/", views.user_update_details, name="update_details"),
   path("profile/<int:pk>/customer_update_details/", views.customer_update_details, name="customer_update_details"),
   path("reset_password/password-token/<str:uid>/<str:token>", views.reset_password, name="reset_password"),
   path("reset_password/", auth_views.PasswordResetView.as_view(template_name='accounts/password_rest.html'), name='reset_password'),
   # path("reset_password_sent/", auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_rest_sent.html'), name='reset_password'),
   # path("reset_password/", auth_views.PasswordResetView.as_view(template_name='accounts/password_rest.html'), name='reset_password'),
   path("profile/<int:pk>/change_password/", views.change_password, name="change_password"),
   path("logout", views.user_sign_out, name="log_out")
   
]
