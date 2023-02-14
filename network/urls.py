
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("following", views.following, name="following"),
    path("profile/<int:user_id>", views.profile, name="profile"),    
    path("follow/<int:user_id>", views.follow, name="follow"),    
    path("post", views.post, name="post"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("like/<int:post_id>", views.like, name="like"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

#    path("emails/<int:email_id>", views.email, name="email"),
]
