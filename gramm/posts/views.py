from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormMixin
from posts.models import Post, PostTags, Comments, Upvote
from socialnet.models import Following, Account, PostImages
from posts.forms import PostForm, TagForm, CommentsForm
from socialnet.forms import ImageForm

import trafaret as tr


LOGIN_URL = "/user/login/"


class MainPage(ListView):
    model = Post
    template_name = "main_page.html"
    allow_empty = False

    def get_queryset(self):
        return Post.objects.select_related("author").all()[:100]


class PostByUserId(LoginRequiredMixin, ListView):
    login_url = LOGIN_URL
    redirect_field_name = "login"
    model = Post
    template_name = "main_page.html"
    allow_empty = False

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        tr.Int().check(user_id)
        return Post.objects.select_related("author").filter(author__id=user_id).all()[:100]


class FollowPost(LoginRequiredMixin, ListView):
    login_url = LOGIN_URL
    redirect_field_name = "login"
    model = Post
    template_name = "main_page.html"

    def get_queryset(self):
        return Post.objects.select_related("author").all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(FollowPost, self).get_context_data(**kwargs)

        follow = Following.objects.filter(follow=self.request.user).all()
        queryset = self.get_queryset()
        post_dict = {}
        for post in queryset:
            post_dict.setdefault(post.author.id, []).append(post)
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
        tr.Int().check(post_id)
        return Post.objects.get(id=post_id)

    def post(self, request, *args, **kwargs):
        comment_form = CommentsForm(request.POST)
        if comment_form.is_valid():
            comment_form.save(commit=False)
            comment_form.instance.author = self.request.user
            post_id = self.kwargs.get("post_id")
            tr.Int().check(post_id)
            comment_form.instance.post = Post.objects.get(id=post_id)
            comment = comment_form.save()
            return HttpResponseRedirect(comment.get_absolute_url())
        else:
            return redirect("main")

    def get_context_data(self, **kwargs):
        context = super(ViewPost, self).get_context_data(**kwargs)
        post_id = self.kwargs.get("post_id")
        tr.Int().check(post_id)
        try:
            image = PostImages.objects.get(post__id=post_id)
        except PostImages.DoesNotExist:
            image = None
        context["form"] = self.form_class
        context["img"] = image
        context["comments"] = Comments.objects.filter(post__id=post_id).all()
        context["upvotes"] = Upvote.objects.filter(post__id=post_id).all()
        me = Account.objects.get(id=self.request.user.id)
        post = self.get_object()
        try:
            u = Upvote.objects.get(account=me, post=post)
        except Upvote.DoesNotExist:
            u = None
        context["upvote"] = u
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
    try:
        u = Upvote.objects.get(account_id=request.user.id, post_id=post_id)
    except Upvote.DoesNotExist:
        u = None
    if u:
        Upvote.objects.filter(account_id=request.user.id, post_id=post_id).delete()
    else:
        Upvote.objects.create(account_id=request.user.id, post_id=post_id)
    return redirect("view_post", post_id=post_id)