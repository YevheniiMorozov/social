from django.urls import path

from posts.views import *


urlpatterns = [
    path("", MainPage.as_view(), name="main"),
    path("follow_post/", FollowPost.as_view(), name="follow_post"),
    path("posts/<int:user_id>/", PostByUserId.as_view(), name="post"),
    path("posts/view_post/<int:post_id>", ViewPost.as_view(), name="view_post"),
    path("posts/view_post/<int:post_id>/upvote", upvote, name="upvote_post"),
    path("posts/view_post/<int:post_id>/downvote", downvote, name="downvote_post"),
    path("profile/add_post/", CreatePost.as_view(), name="create_post"),
]
