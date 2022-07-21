from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from cloudinary.models import CloudinaryField


class Account(AbstractUser):
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    username = models.CharField(max_length=50, unique=False, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "bio"]

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse("profile", kwargs={'user_id': self.id})


from posts.models import Post


class Image(models.Model):
    image = CloudinaryField("image", null=True, default=None, blank=True)
    account = models.ManyToManyField(Account, through="Avatar")
    post = models.ManyToManyField(Post, through="PostImages")


class PostImages(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Avatar(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    @classmethod
    def create(cls, img, user):
        avatar = cls(image=img, account=user)
        return avatar

    class Meta:
        ordering = ["-id"]


class Following(models.Model):
    user = models.ForeignKey(Account, related_name="user", on_delete=models.CASCADE)
    follow = models.ForeignKey(Account, related_name="follow", on_delete=models.CASCADE)

