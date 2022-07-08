from django.urls import path

from .views import *


urlpatterns = [
    path("", MainPage.as_view(), name="main"),
    path("follow_post/", FollowPost.as_view(), name="follow_post"),
    path("posts/<username>/", PostByUsername.as_view(), name="post"),
    path("posts/view_post/<int:post_id>", ViewPost.as_view(), name="view_post"),
    path("posts/view_post/<int:post_id>/upvote", upvote, name="upvote_post"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("register/", register_user, name="register"),
    path("switch_follow/<int:profile_id>", follow_unfollow, name="following"),
    path("profile/<username>", ViewProfile.as_view(), name="profile"),
    path("profile/<username>/followers", FollowerList.as_view(), name="followers"),
    path("profile/user_info/", update_user_info, name="update_user_info"),
    path("profile/add_avatar/", add_avatar, name="add_avatar"),
    path("profile/add_post/", CreatePost.as_view(), name="create_post"),
]
