from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.template.defaultfilters import slugify


class Account(AbstractUser):
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = "user - " + f"{self.email}"
        self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("profile", kwargs={'username': self.slug})


class Post(models.Model):
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("view_post", kwargs={"post_id": self.pk})

    class Meta:
        ordering = ["-created"]


class Image(models.Model):
    image = models.ImageField(upload_to='%Y/%m/%d', blank=True)
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


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name="tag")
    post = models.ManyToManyField(Post, through="PostTags")

    def __str__(self):
        return self.name

    def get_absolut_url(self):
        return reverse("tag", kwargs={"name": self.name})


class PostTags(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(Account, on_delete=models.PROTECT)
    body = models.TextField(max_length=255, verbose_name="comment")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("view_post", kwargs={"post_id": self.post.id})

    class Meta:
        ordering = ["-created"]


class Upvote(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Following(models.Model):
    user = models.ForeignKey(Account, related_name="user", on_delete=models.CASCADE)
    follow = models.ForeignKey(Account, related_name="follow", on_delete=models.CASCADE)

