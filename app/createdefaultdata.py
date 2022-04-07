from .models import Profile
from .models import Order
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .forms import SignUpForm
from random import choice
from string import ascii_uppercase, digits


def PopulateDb():

    User = get_user_model()
    user = User.objects.create_user(
        ("".join(choice(ascii_uppercase + digits) for i in range(10))),
        password=("".join(choice(ascii_uppercase + digits) for i in range(10))),
    )
    user.is_superuser = False
    user.is_staff = False
    user.save()

    user.refresh_from_db()
    user.profile.first_name = "john"
    user.profile.last_name = "lennon"
    user.profile.email = "jlennon@beatles.com"
    user.is_active = True
    user.save()

    ord1 = Order(
        profile=user.profile, price=55000, quantity=1, filled=False, typeorder="sell"
    )
    ord1.save()
    ord2 = Order(
        profile=user.profile, price=45000, quantity=2, filled=False, typeorder="sell"
    )
    ord2.save()
    ord3 = Order(
        profile=user.profile, price=25000, quantity=2, filled=False, typeorder="buy"
    )
    ord3.save()
    ord4 = Order(
        profile=user.profile, price=35000, quantity=3, filled=False, typeorder="buy"
    )
    ord4.save()
