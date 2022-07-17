from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView
from django.http import HttpResponseRedirect, Http404
from django.views.generic.edit import FormMixin
from posts.models import Post, PostTags, Comments, Upvote
from socialnet.models import Following, PostImages, Account
from posts.forms import PostForm, TagForm, CommentsForm
from socialnet.forms import ImageForm

import trafaret as tr
from trafaret import DataError

from collections import defaultdict


LOGIN_URL = "/user/login/"


class MainPage(ListView):
    model = Post
    template_name = "main_page.html"
    allow_empty = True

    def get_queryset(self):
        return Post.objects.select_related("author").all()[:100]


class PostByUserId(LoginRequiredMixin, ListView):
    login_url = LOGIN_URL
    redirect_field_name = "login"
    model = Post
    template_name = "main_page.html"
    allow_empty = True

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        try:
            tr.Int().check(user_id)
        except DataError:
            raise Http404("Invalid data")
        if not (user_id and Account.objects.filter(id=user_id).exists()):
            raise Http404("Post does not exist")
        return Post.objects.select_related("author").filter(author__id=user_id).all()[:100]


class FollowPost(LoginRequiredMixin, ListView):
    login_url = LOGIN_URL
    redirect_field_name = "login"
    model = Post
    template_name = "main_page.html"

    def get_queryset(self):
        return Post.objects.select_related("author").all()[:100]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(FollowPost, self).get_context_data(**kwargs)

        follow = Following.objects.filter(follow=self.request.user).all()
        queryset = [(post.author.id, post) for post in self.get_queryset()]
        post_dict = defaultdict(list)
        for user_id, post in queryset:
            post_dict[user_id].append(post)
        follow_post_list = []
        for item in follow:
            follow_post_list.extend(post_dict[item.user.id])
        context["object_list"] = follow_post_list
        return context


class ViewPost(LoginRequiredMixin, FormMixin, DetailView):
    login_url = LOGIN_URL
    redirect_field_name = "login"
    form_class = CommentsForm
    template_name = "view_post.html"
    pk_url_kwarg = "post_id"
    context_object_name = "post"

    def get_object(self):
        post_id = self.kwargs.get("post_id")
        try:
            tr.Int().check(post_id)
        except DataError:
            raise Http404("Invalid data")
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise Http404("Post does not exist")
        return post

    def post(self, request, *args, **kwargs):
        comment_form = CommentsForm(request.POST)
        if comment_form.is_valid():
            comment_form.save(commit=False)
            comment_form.instance.author = self.request.user
            post_id = self.kwargs.get("post_id")
            try:
                tr.Int().check(post_id)
            except DataError:
                raise Http404("Invalid data")
            comment_form.instance.post = Post.objects.get(id=post_id)
            comment = comment_form.save()
            return HttpResponseRedirect(comment.get_absolute_url())
        else:
            return redirect("main")

    def get_context_data(self, **kwargs):
        context = super(ViewPost, self).get_context_data(**kwargs)
        post_id = self.kwargs.get("post_id")
        try:
            tr.Int().check(post_id)
        except DataError:
            raise Http404("Invalid data")
        context["form"] = self.form_class
        context["img"] = PostImages.objects.filter(post__id=post_id).first()
        context["comments"] = Comments.objects.filter(post__id=post_id).all()
        context["upvotes"] = Upvote.objects.filter(post__id=post_id).all()
        context["upvote"] = Upvote.objects.filter(account__id=self.request.user.id, post__id=post_id).first()
        context["tag"] = PostTags.objects.filter(post=self.get_object()).all()
        return context


class CreatePost(CreateView):
    form_class = PostForm
    form_class_2 = ImageForm
    form_class_3 = TagForm
    template_name = "create_post.html"

    def post(self, request, *args, **kwargs):
        post_form = PostForm(request.POST, request.FILES)
        img_form = ImageForm(request.POST, request.FILES)
        tag_form = TagForm(request.POST, request.FILES)
        if post_form.is_valid() and img_form.is_valid() and tag_form.is_valid():
            post_form.save(commit=False)
            tag_form.save()
            img_form.save()
            post_form.instance.author = self.request.user
            post = post_form.save()
            img_form.instance.post.add(post)
            tag_form.instance.post.add(post)
            return redirect("main")
        else:
            return messages.error(request, "Invalid data")

    def get_context_data(self, **kwargs):
        context = super(CreatePost, self).get_context_data(**kwargs)
        context["post"] = self.form_class
        context["img"] = self.form_class_2
        context["tag"] = self.form_class_3
        return context

    def form_valid(self, **kwargs):
        return super(CreatePost, self).form_valid(**kwargs)


@login_required
def upvote(request, post_id):
    if request.method == "POST":
        if not Post.objects.filter(id=post_id).exists():
            raise Http404("Post does not exist")
        deleted = Upvote.objects.filter(account_id=request.user.id, post_id=post_id).delete()
        # deleted return tuple (int, {})
        if deleted[0] == 0:
            Upvote.objects.create(account_id=request.user.id, post_id=post_id)
        return redirect("view_post", post_id=post_id)