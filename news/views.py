import logging
from datetime import datetime

from django.contrib import auth
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render

from news import utils
from news.models import CustomUser
from news.models import Headline

logger = logging.getLogger("__main__")


def scrape(request):
    utils.scrape_news()
    utils.update_news_vector()
    return redirect("home")


def index(request):
    random_three = Headline.objects.order_by("-id")[1:4]
    latest_all_news = Headline.objects.order_by("-id")[4:]
    latest_news = Headline.objects.order_by("-id")[0]

    clean_text = "No Data. Please Click Fetch News Above"
    if latest_news:
        clean_text = latest_news.description

    context = {
        "head": latest_news,
        "random_three": random_three,
        "latest_all_news": latest_all_news,
        "clean_text": clean_text,
        "date": datetime.now(),
        "authenticated": request.user.is_authenticated,
    }

    return render(request, "news/index.html", context)


# register,login and logout using bultin django authication
def user_register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        if CustomUser.objects.filter(username=username).exists():
            return render(
                request,
                "news/register.html",
                {"error": "Username is already taken", "date": datetime.now()},
            )
        else:
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            auth.login(request, user)
            return redirect("home")
    else:
        return render(request, "news/register.html", {"date": datetime.now()})


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("home")
        else:
            return render(
                request,
                "news/login.html",
                {"error": "Invalid credentials", "date": datetime.now()},
            )
    else:
        return render(request, "news/login.html", {"date": datetime.now()})


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect("home")


def get_similar_news(request, news_id):
    if not request.user.is_authenticated:
        return redirect("login")

    logger.info("Getting Similar News")
    similar_news = utils.get_similar_news(news_id)
    latest_news = similar_news[0]
    random_three = similar_news[1:4]
    other_similar_news = similar_news[4:]
    clean_text = "No Data. Please Click Fetch News Above"
    if latest_news:
        clean_text = latest_news.description
    context = {
        "head": latest_news,
        "random_three": random_three,
        "latest_all_news": other_similar_news,
        "clean_text": clean_text,
        "date": datetime.now(),
        "authenticated": request.user.is_authenticated,
    }

    return render(request, "news/index.html", context)


def search_news(request, search_text):
    if not request.user.is_authenticated:
        return redirect("login")

    logger.info("Searching News")
    searched_news = Headline.objects.filter(
        description__icontains=search_text
    ).order_by("-id")
    latest_news, latest_all_news, random_three = list(), list(), list()
    if searched_news:
        latest_news = searched_news[0]
    if len(searched_news) > 3:
        random_three = searched_news[1:4]
    if len(searched_news) > 4:
        latest_all_news = searched_news[4:]

    clean_text = "No News Found. Please try searching other news"
    if latest_news:
        clean_text = latest_news.description

    context = {
        "head": latest_news,
        "random_three": random_three,
        "latest_all_news": latest_all_news,
        "clean_text": clean_text,
        "date": datetime.now(),
        "authenticated": request.user.is_authenticated,
    }

    return render(request, "news/index.html", context)
