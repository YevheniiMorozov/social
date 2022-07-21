from django.db import models
from socialnet.models import Account
from django.urls import reverse


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


class Downvote(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
