from django.contrib import admin
from .models import User, Category, Item, Bid, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Bid)
admin.site.register(Comment)