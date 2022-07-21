import random
from string import ascii_letters
from socialnet.models import Account, Post, PostImages, Avatar, Image, Following
from posts.models import Comments, Tag, PostTags, Upvote, Downvote
from django.core.management.base import BaseCommand, CommandError


def random_string(length):
    return "".join(random.choices(population=ascii_letters, k=length))


def add_to_db_random_value():
    firstname = ["Andrew", "Den", "John", "Ann", "Mary", "Molly"]
    lastname = ["Edison", "Brown", "Black", "White", "Snow", "Lincoln"]

    text = """
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
            magna aliqua. Lorem ipsum dolor sit amet. Vel eros donec ac odio tempor orci. Consectetur adipiscing elit ut
            aliquam purus sit. Vulputate eu scelerisque felis imperdiet proin fermentum leo vel orci. Luctus accumsan tortor
            posuere ac ut consequat semper. Turpis egestas maecenas pharetra convallis posuere morbi leo urna.
            Cursus metus aliquam eleifend mi in nulla posuere sollicitudin. Tincidunt augue interdum velit euismod in
            pellentesque massa placerat duis. Auctor elit sed vulputate mi sit. Non enim praesent elementum facilisis.
            Tortor at risus viverra adipiscing at. Diam maecenas sed enim ut. Velit dignissim sodales ut eu sem integer 
            vitae. Malesuada fames ac turpis egestas. Etiam dignissim diam quis enim lobortis scelerisque. Tortor id aliquet
            lectus proin nibh nisl condimentum id. Cursus metus aliquam eleifend mi in nulla posuere. Sit amet mauris 
            commodo quis imperdiet massa tincidunt. Diam vel quam elementum pulvinar etiam non quam. Diam vel quam elementum
            pulvinar etiam non quam lacus. Eget felis eget nunc lobortis. Tellus rutrum tellus pellentesque eu tincidunt 
            tortor. Et netus et malesuada fames ac turpis.
            """

    users = [Account(
                     first_name=random.choice(firstname),
                     last_name=random.choice(lastname),
                     email=random_string(5) + "@" + random_string(4) + ".com",
                     password=random_string(15),
                     bio=text
                     ) for _ in range(1, 13)]

    Account.objects.bulk_create(users)

    tags = [Tag(name=random.choice(text.split())) for _ in range(3)]

    Tag.objects.bulk_create(tags)

    posts = [Post(title="".join(random.choice(text.split())),
                  description=" ".join(random.choices(population=text.split(), k=random.randint(20, 50))),
                  author=random.choice(users)
                  ) for _ in range(12)]

    Post.objects.bulk_create(posts)

    post_tags = [PostTags(post=random.choice(posts),
                          tag=random.choice(tags)) for _ in range(15)]

    PostTags.objects.bulk_create(post_tags)

    comments = [Comments(body=" ".join(random.choices(population=text.split(), k=random.randint(3, 15))),
                         author=random.choice(users),
                         post=random.choice(posts)
                  ) for _ in range(18)]

    Comments.objects.bulk_create(comments)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("fake_data", nargs='+', type=str)

    def handle(self, *args, **options):
        PostImages.objects.all().delete()
        Avatar.objects.all().delete()
        Image.objects.all().delete()
        PostTags.objects.all().delete()
        Tag.objects.all().delete()
        Post.objects.all().delete()
        Upvote.objects.all().delete()
        Downvote.objects.all().delete()
        Comments.objects.all().delete()
        Following.objects.all().delete()
        Account.objects.all().delete()

        if options["fake_data"]:
            add_to_db_random_value()
            self.stdout.write(self.style.SUCCESS("Successfully create"))
        else:
            CommandError("Error")

