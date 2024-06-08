from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from model_utils.models import TimeStampedModel


class CustomRequestManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(delete=False)


class User(AbstractUser, TimeStampedModel):
    first_name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    friends = models.ManyToManyField("self", blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "username"]

    def __str__(self):
        return f"{self.username}"

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("email"),
                name="Case Insensitive Email Unique Constraint",
            ),
        ]


class FriendRequest(TimeStampedModel):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    accepted = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    objects = CustomRequestManager()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["from_user", "to_user"],
                name="unique_friend_request",
            ),
        ]

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}"
