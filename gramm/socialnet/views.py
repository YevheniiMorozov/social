from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import FormMixin
from .forms import UserLoginForm, UserRegisterForm, AccountRegisterForm, ImageForm, PostForm, TagForm, CommentsForm
from .models import Account, Post, Avatar, PostImages, Comments, Following, Upvote, PostTags


def login_user(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("profile", user.username)
    else:
        form = UserLoginForm()
    return render(request, "login.html", {"form": form})


def logout_user(request):
    logout(request)
    return redirect("login")


def register_user(request):
    if request.method == "POST":
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Success!")
            return redirect("update_user_info")
        else:
            messages.error(request, "Invalid data, please try again")
    else:
        form = AccountRegisterForm()
        return render(request, "register.html", {"form": form})


@login_required
def update_user_info(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST, instance=request.user)
        if form.is_valid():
            Account.objects.filter(email=request.user.email).update(
                first_name=request.POST.get("first_name"),
                last_name=request.POST.get("last_name"),
                password=make_password(request.POST.get("password")),
                username=request.POST.get("username"),
                bio=request.POST.get("bio"),
                slug=request.POST.get("username")
            )
            login(request, Account.objects.get(email=request.user.email))
            messages.success(request, "Success!")
            return redirect("main")
        else:
            messages.error(request, "Invalid data, please try again")
    else:
        form = UserRegisterForm()
        return render(request, "update_user_profile.html", {"form": form})


class ViewProfile(LoginRequiredMixin, DetailView):
    login_url = "/login/"
    redirect_field_name = "login"
    template_name = "profile.html"
    slug_url_kwarg = "account_slug"
    context_object_name = "profile"

    def get_object(self):
        queryset = Account.objects.get(username=self.kwargs.get("username"))
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(ViewProfile, self).get_context_data(**kwargs)
        context["post"] = Post.objects.filter(author__username=self.kwargs.get("username")).all()
        context["img"] = Avatar.objects.filter(account__username=self.kwargs.get("username")).first()
        context["all_images"] = Avatar.objects.filter(account__username=self.kwargs.get("username")).all()
        context["follower"] = Following.objects.filter(user__username=self.kwargs.get("username")).all()
        view_profile = self.get_object()
        my_profile = Account.objects.get(id=self.request.user.id)
        try:
            follow = Following.objects.get(user=view_profile, follow=my_profile)
        except Following.DoesNotExist:
            follow = None
        context["follow"] = follow
        return context


@login_required
def add_avatar(request):
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form.instance.account.add(request.user)
            return redirect("profile", request.user.username)
        else:
            messages.error(request, "Invalid data, please try again")
    else:
        form = ImageForm()
        return render(request, "add_avatar.html", {"form": form})


class MainPage(ListView):
    model = Post
    template_name = "main_page.html"
    allow_empty = False

    def get_queryset(self):
        return Post.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MainPage, self).get_context_data()

        context["image"] = PostImages.objects.all()
        context["object_list"] = Post.objects.all()
        return context


class PostByUsername(LoginRequiredMixin, ListView):
    login_url = "/login/"
    redirect_field_name = "login"
    model = Post
    template_name = "main_page.html"
    allow_empty = False

    def get_queryset(self):
        return Post.objects.filter(author__username=self.kwargs.get("username")).all()


class FollowPost(LoginRequiredMixin, ListView):
    login_url = "/login/"
    redirect_field_name = "login"
    model = Following
    template_name = "main_page.html"

    def get_queryset(self):
        return Following.objects.filter(follow=self.request.user).all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(FollowPost, self).get_context_data(**kwargs)
        follow = self.get_queryset()
        follow_post_list = []
        for item in follow:
            follow_post_list.extend(Post.objects.filter(author__id=item.user.id).all())
        context["object_list"] = follow_post_list
        return context


class ViewPost(LoginRequiredMixin, FormMixin, DetailView):
    login_url = "/login/"
    redirect_field_name = "login"
    form_class = CommentsForm
    template_name = "view_post.html"
    pk_url_kwarg = "post_id"
    context_object_name = "post"

    def get_object(self):
        return Post.objects.get(id=self.kwargs.get("post_id"))

    def post(self, request, *args, **kwargs):
        comment_form = CommentsForm(request.POST)
        if comment_form.is_valid():
            comment_form.save(commit=False)
            comment_form.instance.author = self.request.user
            # Хотел сделать self.get_object чтобы не повторяться, но тогда почему-то ломалась форма
            comment_form.instance.post = Post.objects.get(id=self.kwargs.get("post_id"))
            comment = comment_form.save()
            return HttpResponseRedirect(comment.get_absolute_url())
        else:
            return redirect("main")
    
    def get_context_data(self, **kwargs):
        context = super(ViewPost, self).get_context_data(**kwargs)
        try:
            image = PostImages.objects.get(post__id=self.kwargs.get("post_id"))
        except PostImages.DoesNotExist:
            image = None
        context["form"] = self.form_class
        context["img"] = image
        context["comments"] = Comments.objects.filter(post__id=self.kwargs.get("post_id")).all()
        context["upvotes"] = Upvote.objects.filter(post__id=self.kwargs.get("post_id")).all()
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


class FollowerList(LoginRequiredMixin, ListView):
    login_url = "/login/"
    redirect_field_name = "login"
    model = Following
    template_name = "profile_list.html"
    context_object_name = "profiles"

    def get_queryset(self, *args, **kwargs):
        return Following.objects.filter(user__username=self.kwargs.get("username")).all()


@login_required
def follow_unfollow(request, profile_id):
    me = Account.objects.get(id=request.user.id)
    not_me = Account.objects.get(id=profile_id)
    try:
        f = Following.objects.get(user=not_me, follow=me)
    except Following.DoesNotExist:
        f = None
    if f:
        Following.objects.filter(user=not_me, follow=me).delete()
    else:
        Following.objects.create(user=not_me, follow=me)
    return redirect("profile", username=not_me.username)


@login_required
def upvote(request, post_id):
    me = Account.objects.get(id=request.user.id)
    post = Post.objects.get(id=post_id)
    try:
        u = Upvote.objects.get(account=me, post=post)
    except Upvote.DoesNotExist:
        u = None
    if u:
        Upvote.objects.filter(account=me, post=post).delete()
    else:
        Upvote.objects.create(account=me, post=post)
    return redirect("view_post", post_id=post_id)