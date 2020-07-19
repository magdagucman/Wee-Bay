from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("listed/<int:item_id>", views.listed, name="listed"),
    path ("watchlist", views.watchlist, name="watchlist"),
    path ("add/<int:item_id>", views.add, name="add"),
    path ("remove/<int:item_id>", views.remove, name="remove"),
    path ("categories", views.categories, name="categories"),
    path ("category/<int:category_id>", views.category, name="category"),
    path ("close/<int:item_id>", views.close, name="close"),
    path ("comment/<int:item_id>", views.comment, name="comment")
]
