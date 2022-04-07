from django.contrib.auth import login, authenticate
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .models import Profile, Order
from .forms import SignUpForm
import json
import requests
from .createdefaultdata import PopulateDb


class Bot:
    def __init__(self):
        ''' api for get current btc price from coinmarketcap.
        i should hide API KEY by saving it in another file and dont upload it on github'''
        self.url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        self.params = {"start": "1", "limit": "1", "convert": "USD"}
        self.headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": "67ba26f2-78d4-4e2d-bfb4-7f393fca851b",
        }

    def fetchCurrenciesData(self):
        r = requests.get(url=self.url, headers=self.headers, params=self.params).json()
        return r["data"]


def createdata(request):
    PopulateDb()
    return HttpResponseRedirect("/")


def home_view(request):
    return render(request, "home.html")


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.first_name = form.cleaned_data.get("first_name")
            user.profile.last_name = form.cleaned_data.get("last_name")
            user.profile.email = form.cleaned_data.get("email")
            user.is_active = True
            user.save()

            login(request, user)
            return render(request, "home.html")

    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


def balance_view(request):
    my_orders_current_open = reversed(
        Order.objects.filter(profile=request.user.profile, filled=False)
    )
    my_orders_closed = reversed(
        Order.objects.filter(profile=request.user.profile, filled=True)
    )
    total_balance = 0
    currencies = Bot().fetchCurrenciesData()
    btc_value = round(currencies[0]["quote"]["USD"]["price"], 2)
    total_balance = round(
        request.user.profile.usd + (request.user.profile.bitcoin * btc_value), 2
    )

    #add open orders to the balance, cause it is locked capital
    for open_order in Order.objects.filter(profile=request.user.profile, filled=False):
        if open_order.typeorder == "buy":
            total_balance += open_order.quantity * open_order.price
        elif open_order.typeorder == "sell":
            total_balance += open_order.quantity

    variation_btc = 0
    variation_usd = 0

    # determinate the balance's variation from closed orders
    for closed_order in Order.objects.filter(profile=request.user.profile, filled=True):
        if closed_order.typeorder == "buy":
            # + btc - usd
            variation_btc += closed_order.quantity
            variation_usd -= closed_order.quantity * closed_order.price
        elif closed_order.typeorder == "sell":
            # - btc + usdt
            variation_btc -= closed_order.quantity
            variation_usd += closed_order.quantity * closed_order.price

    try:
        difference_btc_since_start = round(
            (variation_btc / (request.user.profile.bitcoin - variation_btc) * 100), 2
        )
    except:
        difference_btc_since_start = -100

    if difference_btc_since_start > 0:
        difference_btc_since_start = "+" + str(difference_btc_since_start)

    try:
        difference_usd_since_start = round(
            (variation_usd / (request.user.profile.usd - variation_usd) * 100), 2
        )
    except:
        difference_usd_since_start = -100

    if difference_usd_since_start > 0:
        difference_usd_since_start = "+" + str(difference_usd_since_start)


    '''could determinate total balance variaton by calculating btc's average load price between
    initial deposit ( random value) and closed buy orders'''
    return render(
        request,
        "balance.html",
        {
            "user": request.user.profile,
            "my_orders_current_open": my_orders_current_open,
            "my_orders_closed": my_orders_closed,
            "total_balance": total_balance,
            "difference_btc_since_start": difference_btc_since_start,
            "difference_usd_since_start": difference_usd_since_start,
        },
    )


def cancel_order_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.typeorder == "buy":
        request.user.profile.usd += order.quantity * order.price
    elif order.typeorder == "sell":
        request.user.profile.bitcoin += order.quantity

    request.user.profile.save()
    order.delete()
    return HttpResponseRedirect("/balance")


def book_order_view(request):

    buy_orders = Order.objects.filter(filled=False, typeorder="buy").order_by("-price")
    sell_orders = Order.objects.filter(filled=False, typeorder="sell").order_by(
        "-price"
    )

    currencies = Bot().fetchCurrenciesData()
    btc_value = round(currencies[0]["quote"]["USD"]["price"], 2)
    return render(
        request,
        "bookorder.html",
        {"buy_orders": buy_orders, "sell_orders": sell_orders, "btc_value": btc_value},
    )


def place_new_order_view(request):
    return render(request, "placeneworder.html", {"user": request.user.profile})


def place_order_request_view(request):
    if request.method == "GET":
        new_order = Order()

        #creating new order 
        new_order.profile = request.user.profile
        new_order.price = float(request.GET["price"])
        new_order.quantity = float(request.GET["qty"])
        new_order.typeorder = request.GET["type"]

        message = ""

        if new_order.typeorder == "buy":
            # check if enought usd in the wallet
            print("i am buying")
            if request.user.profile.usd >= (new_order.quantity * new_order.price):
                print("ho abbastanza soldi")
                new_order.save()

                # searching some selling orders
                selling_order = (
                    Order.objects.filter(
                        typeorder="sell",
                        price__lte=new_order.price,
                        quantity=new_order.quantity,
                    )
                    .order_by("price")
                    .first()
                )
                if selling_order is not None:
                    seller_profile = Profile.objects.filter(
                        _id=selling_order.profile._id
                    ).first()
                    print("ho trovato un ordine")

                    # add btc to user
                    request.user.profile.bitcoin += new_order.quantity
                    request.user.profile.usd -= (
                        selling_order.quantity * selling_order.price
                    )
                    request.user.profile.save()
                    new_order.price = selling_order.price
                    new_order.filled = True
                    new_order.save()

                    # add usd to seller
                    seller_profile.usd += selling_order.quantity * selling_order.price
                    seller_profile.save()
                    selling_order.filled = True
                    selling_order.save()

                    message = "Order filled correctly."
                else:
                    request.user.profile.usd -= new_order.quantity * new_order.price
                    request.user.profile.save()
                    new_order.save()

                    message = "Order placed on the Order Book"

        else:  # selling order
            # check if enought btc in the wallet
            if request.user.profile.bitcoin >= new_order.quantity:

                new_order.save()

                # searching some buying orders
                buying_order = (
                    Order.objects.filter(
                        typeorder="buy",
                        price__gte=new_order.price,
                        quantity=new_order.quantity,
                    )
                    .order_by("price")
                    .first()
                )
                if buying_order is not None:
                    buyer_profile = Profile.objects.filter(
                        _id=buying_order.profile._id
                    ).first()

                    # add usd to user
                    request.user.profile.bitcoin -= new_order.quantity
                    request.user.profile.usd += (
                        buying_order.quantity * buying_order.price
                    )
                    request.user.profile.save()
                    new_order.price = buying_order.price
                    new_order.filled = True
                    new_order.save()

                    # add btc to buyer
                    buyer_profile.bitcoin += buying_order.quantity
                    buyer_profile.save()
                    buying_order.filled = True
                    buying_order.save()

                    message = "Order filled correctly."
                else:
                    request.user.profile.bitcoin -= new_order.quantity
                    request.user.profile.save()
                    new_order.save()

                    message = "Order placed on the Order Book"

        return render(request, "home.html", {"message": message})

    return render(request, "placeneworder.html", {"user": request.user.profile})
