from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserLoginForm, UserRegisterForm, AccountRegisterForm, ImageForm
from posts.models import Post
from .models import Account, Avatar, Following

import trafaret as tr

LOGIN_URL = "login"


def login_user(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("profile", user.id)
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
            return redirect('update_user_info')
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
            )
            login(request, Account.objects.get(email=request.user.email))
            messages.success(request, "Success!")
            return redirect("main")
        else:
            messages.error(request, "Invalid data, please try again")
    else:
        form = UserRegisterForm()
        return render(request, "update_user_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect("main")
        else:
            messages.error(request, "Invalid data, please try again")
            return redirect("add_avatar")
    else:
        form = PasswordChangeForm(user=request.user)
        return render(request, "pass.html", {"form": form})


class ViewProfile(LoginRequiredMixin, DetailView):
    login_url = LOGIN_URL
    redirect_field_name = "login"
    template_name = "profile.html"
    context_object_name = "profile"

    def get_object(self):
        user_id = self.kwargs.get("user_id")
        tr.Int().check(user_id)
        return Account.objects.get(id=user_id)

    def get_context_data(self, *args, **kwargs):
        context = super(ViewProfile, self).get_context_data(**kwargs)
        user_id = self.kwargs.get("user_id")
        tr.Int().check(user_id)
        context["post"] = Post.objects.filter(author__id=user_id).all()
        context["img"] = Avatar.objects.filter(account__id=user_id).first()
        context["all_images"] = Avatar.objects.filter(account__id=user_id).all()
        context["follower"] = Following.objects.filter(user__id=user_id).all()
        try:
            follow = Following.objects.get(user__id=user_id, follow__id=self.request.user.id)
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
            return redirect("profile", request.user.id)
        else:
            messages.error(request, "Invalid data, please try again")
    else:
        form = ImageForm()
        return render(request, "add_avatar.html", {"form": form})


class FollowerList(LoginRequiredMixin, ListView):
    login_url = LOGIN_URL
    redirect_field_name = "login"
    model = Following
    template_name = "profile_list.html"
    context_object_name = "profiles"

    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        tr.Int().check(user_id)
        return Following.objects.filter(user__id=user_id).all()


@login_required
def follow_unfollow(request, profile_id):
    try:
        f = Following.objects.get(user_id=profile_id, follow_id=request.user.id)
    except Following.DoesNotExist:
        f = None
    if f:
        Following.objects.filter(user_id=profile_id, follow_id=request.user.id).delete()
    else:
        Following.objects.create(user_id=profile_id, follow_id=request.user.id)
    return redirect("profile", user_id=profile_id)

