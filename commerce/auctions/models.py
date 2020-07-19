from django.contrib.auth.models import AbstractUser
from django.db import models


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    items = models.ManyToManyField('Item', blank=True, related_name="items")
    def __str__(self):
        return f"{self.name}"

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    image = models.URLField(default="https://cdn.pixabay.com/photo/2015/07/19/11/05/panels-851426_1280.jpg")
    price = models.DecimalField(decimal_places=2, max_digits=32)
    seller = models.ForeignKey('User', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    current_bid = models.DecimalField(decimal_places=2, max_digits=32, default=0)
    closed = models.BooleanField(default=False)
    comments = models.ManyToManyField('Comment', blank=True, related_name="comments")
    def __str__(self):
        return f"{self.title}"

class User(AbstractUser):
    my_watchlist = models.ManyToManyField(Item, blank=True, related_name="watched_items")

class Bid(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    bid = models.DecimalField(decimal_places=2, max_digits=32)

class Comment(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=150)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return f"{self.comment}"
    