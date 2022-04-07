from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from djongo.models.fields import ObjectIdField, Field
import numpy as np


class Profile(models.Model):
    _id = ObjectIdField()
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=150)
    ips = models.Field(default=[])
    subprofile = models.Field(default={})
    bitcoin = models.FloatField(default=np.random.randint(10))
    usd = models.FloatField(default=100000)

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Order(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    quantity = models.FloatField()
    filled = models.BooleanField(default=False)

    CATEGORY_CHOICES = (
        ("buy", "buy"),
        ("sell", "sell"),
    )
    typeorder = models.CharField(max_length=4, choices=CATEGORY_CHOICES)
