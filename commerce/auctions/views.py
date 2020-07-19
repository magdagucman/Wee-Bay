from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import User, Category, Item, Bid, Comment

# Create a list of categories
CHOICES = []
for cat in Category.objects.all():
    CHOICES.append((cat.id, cat.name))

CATEGORIES = Category.objects.all()

# A form for listing new items    
class ItemForm(forms.Form):
    title = forms.CharField(label="", max_length=64, widget=forms.TextInput(attrs={'class' : 'form-control', 'name': "title", 'placeholder': "Title", 'autocomplete': 'off'}))
    price = forms.DecimalField(label="", decimal_places=2, max_digits=32, widget=forms.NumberInput(attrs={'class' : 'form-control', 'name': "price", 'placeholder': "Minimum Price", 'autocomplete': 'off'}))
    description = forms.CharField(label="", max_length=500, widget=forms.Textarea(attrs={'class': "form-control", 'name': "description", 'placeholder': "Describe Your Item"}))
    category = forms.ChoiceField(choices=CHOICES, required=False, label="", widget=forms.Select(attrs={'class': 'form-control', 'name': "category", 'placeholder': "Category", 'autocomplete': 'off'}))
    image = forms.URLField(max_length=1000, label="", required=False, empty_value="https://cdn.pixabay.com/photo/2015/07/19/11/05/panels-851426_1280.jpg", widget=forms.TextInput(attrs={'class' : 'form-control', 'name': "image", 'placeholder': "Image URL (optional)", 'autocomplete': 'off'}))

# A form for making bids
class BidForm(forms.Form):
    bid = forms.DecimalField(label="", decimal_places=2, max_digits=32, widget=forms.NumberInput(attrs={'class' : 'form-control inline', 'name': "bid", 'placeholder': "Your Bid"}))

# A form for comments
class CommentForm(forms.Form):
    comment = forms.CharField(label="", max_length=150, widget=forms.TextInput(attrs={'class': 'form-control inline', 'id': 'comment', 'name': "comment", 'placeholder': "Leave a Comment"}))


def index(request):
    return render(request, "auctions/index.html", {
        "items": Item.objects.all(),
        "categories": CATEGORIES
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password.",
                "categories": CATEGORIES
            })
    else:
        return render(request, "auctions/login.html", {
            "categories": CATEGORIES
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match.",
                "categories": CATEGORIES
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken.",
                "categories": CATEGORIES
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html", {
            "categories": CATEGORIES
        })

@login_required
def create_listing(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        
        # Ensure server-side form validation
        if form.is_valid():
            title = form.cleaned_data["title"]
            price = form.cleaned_data["price"]
            description = form.cleaned_data["description"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]

            # Create new item and save it in database, then save it
            i = Item(title=title, price=price, description=description, category=Category(category), image=image, seller=request.user)
            i.save()

            # Add the item to a list of items in chosen category, then save it
            cat = Category.objects.get(id=category)
            cat.items.add(i.id)
            cat.save()

            return HttpResponseRedirect(reverse("index"))

        # If form is invalid, display it along with a message saying so
        else:
            return render(request, "auctions/create.html", {
                "form": form,
                "message": "Form invalid, try again.",
                "categories": CATEGORIES
            })
    else:
        return render(request, "auctions/create.html", {
            "form": ItemForm(),
            "message": "",
            "categories": CATEGORIES
        })


def listed(request, item_id):
    item = Item.objects.get(id=item_id)
    comments = item.comments.all()
    watched = False
    winner=""

    if request.user.id:
        user = User.objects.get(id=request.user.id)
        # Check whether the listing is in current user's watchlist
        if item in user.my_watchlist.all():
            watched = True

    # Check whether the listing is still active. If not, update the winner variable
    if item.closed:
        if item.current_bid >= item.price:
            bid = Bid.objects.get(item=item_id, bid=item.current_bid)
            winner = bid.buyer
    

    if request.method == "POST":
        form = BidForm(request.POST)

        # Ensure server-side form validation
        if form.is_valid():
            bid = form.cleaned_data["bid"]

            # Check if the bid is high enough
            if bid > item.current_bid and bid >= item.price:

                # Update the current bid field for the item, then save it
                item.current_bid = bid
                item.save()

                # Create new bid object, then save it
                new_bid = Bid(item=item, buyer=request.user, bid=bid)
                new_bid.save()

                return render(request, "auctions/listed.html", {
                        "item": item,
                        "form": BidForm(),
                        "comment_form": CommentForm(),
                        "message": "Your bid was succesfully saved!",
                        "watched": watched,
                        "winner": winner,
                        "comments": comments,
                        "categories": CATEGORIES
                    })
            else:
                return render(request, "auctions/listed.html", {
                        "item": item,
                        "form": BidForm(),
                        "comment_form": CommentForm(),
                        "message": "Your bid is too low!",
                        "watched": watched,
                        "winner": winner,
                        "comments": comments,
                        "categories": CATEGORIES
                    })
        else:
            return render(request, "auctions/listed.html", {
                        "item": item,
                        "form": bid,
                        "comment_form": CommentForm(),
                        "message": "Invalid input, try again!",
                        "watched": watched,
                        "winner": winner,
                        "comments": comments,
                        "categories": CATEGORIES
                    })
    else:
        return render(request, "auctions/listed.html", {
                        "item": item,
                        "form": BidForm(),
                        "comment_form": CommentForm(),
                        "watched": watched,
                        "winner": winner,
                        "comments": comments,
                        "categories": CATEGORIES
                    })

@login_required
def watchlist(request):
    user = User.objects.get(id=request.user.id)
    items = user.my_watchlist.all()

    return render(request, "auctions/watchlist.html", {
                        "items": items,
                        "categories": CATEGORIES
                    })

@login_required
def add(request, item_id):

    # Select current user object from database, add the item to watchlist, then save it
    user = User.objects.get(id=request.user.id)
    user.my_watchlist.add(item_id)
    user.save()
    return HttpResponseRedirect(reverse("listed", kwargs={"item_id": item_id}))

@login_required
def remove(request, item_id):

    # Select current user object from database, remove the item from watchlist, then save it
    user = User.objects.get(id=request.user.id)
    user.my_watchlist.remove(item_id)
    user.save()
    return HttpResponseRedirect(reverse("listed", kwargs={"item_id": item_id}))


def categories(request):
    return render(request, "auctions/categories.html", {
                        "categories": CATEGORIES
                    })

def category(request, category_id):

    # Select the requested category object
    category = Category.objects.get(id=category_id)

    # Create a variable with all items in the category
    category_list = category.items.all()

    # Check if there is at least one active item in category
    exists = False
    for item in category_list:
        if item.closed == False:
            exists = True
    if not exists:
        category_list = []
    return render(request, "auctions/category.html", {
                        "category_list": category_list,
                        "category": category,
                        "categories": CATEGORIES
                    })

@login_required
def close(request, item_id):
    item = Item.objects.get(id=item_id)
    user = request.user.id

    # Ensure person who tries to close the auction is its creator
    if item.seller.id == user:
        item.closed = True
        item.save()
        return HttpResponseRedirect(reverse("listed", kwargs={"item_id": item_id}))
    else:
        return HttpResponseRedirect(reverse("listed", kwargs={"item_id": item_id}))

@login_required
@require_POST
def comment(request, item_id):
    form = CommentForm(request.POST)
    item = Item.objects.get(id=item_id)
    user = User.objects.get(id=request.user.id)

    # Ensure the form is valid
    if form.is_valid():
        comment = form.cleaned_data["comment"]

        # Create new Comment object, then save it
        new_comment = Comment(comment=comment, commenter=user, item=item)
        new_comment.save()

        # Add the comment to a list of comments for the item
        item.comments.add(new_comment)
        item.save()
        return HttpResponseRedirect(reverse("listed", kwargs={"item_id": item_id}))
    else:
        render(request, "auctions/listed.html", {
                        "item": item,
                        "form": BidForm(),
                        "comment_form": comment,
                        "watched": watched,
                        "winner": winner,
                        "comments": comments,
                        "comment_message": "Invalid input, try again!",
                        "categories": CATEGORIES
                    })