from django import template

register = template.Library()


@register.filter(name="sub")
def sub(upvote, downvote):
    return upvote - downvote