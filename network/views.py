from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
import datetime
import json
from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt

from .models import User, Post


def post(request):
    if request.method == "POST":
        new_post = Post()
        new_post.content = request.POST.get('content')
        new_post.author = request.user
        new_post.created = datetime.datetime.now()
        new_post.save()
    return HttpResponseRedirect(reverse("index"))


# @csrf_exempt - added csrf in js Cookie
def edit(request, post_id):

    # Query for requested post
    try:
        edpost = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Update post
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("edpost") is not None:
            edpost.content = data["edpost"]
        edpost.save()
        return HttpResponse(status=204)  # нужен return, без него (хоть с пустым return, хоть вообще без return - ошибка 500, но работает

    # Update must be via PUT
    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)


@login_required
def like(request, post_id):
    # Query for requested post
    try:
        likedpost = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Update post
    if request.method == "PUT":
        r = request.user
        if r in likedpost.liked.all():
            likedpost.liked.remove(r)
        else:
            likedpost.liked.add(r)
        # попробуем не сохранять
        return HttpResponse(status=204)


def profile(request, user_id):
    userpage = User.objects.get(pk=user_id)
    r = request.user
    if r.is_authenticated:
        if userpage in r.follows.all():
            followBtn = "Unfollow"
        else:
            followBtn = "Follow"
    else:
        followBtn = "False"
    follows = userpage.follows.all().count()
    followers = User.objects.filter(follows=userpage).count()
    posts = Post.objects.filter(author=userpage).order_by('created').reverse()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html",
                  {"followBtn": followBtn, "follows": follows, "followers": followers, "userpage": userpage, "page_obj": page_obj})


def follow(request, user_id):
    userpage = User.objects.get(pk=user_id)
    r = request.user
    if userpage in r.follows.all():
        r.follows.remove(userpage)
    else:
        r.follows.add(userpage)
    return HttpResponseRedirect(reverse("profile", args=(user_id,)))


def following(request):
    qst = request.user.follows.all()  # qst = User.objects.filter(follows=request.user) - это фоловверы
    posts = Post.objects.filter(author__in=qst).order_by('created').reverse()  # скобочки важны  после reverse, д.б метод
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {"page_obj": page_obj})


def index(request):
    posts = Post.objects.all().order_by('created').reverse()  # скобочки важны  после reverse, д.б метод, вот в {html}  без них
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {"page_obj": page_obj})


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
