# Generated by Django 4.0.5 on 2022-07-11 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
        ('socialnet', '0003_alter_account_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='author',
        ),
        migrations.RemoveField(
            model_name='posttags',
            name='post',
        ),
        migrations.RemoveField(
            model_name='posttags',
            name='tag',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='post',
        ),
        migrations.RemoveField(
            model_name='upvote',
            name='account',
        ),
        migrations.RemoveField(
            model_name='upvote',
            name='post',
        ),
        migrations.RemoveField(
            model_name='account',
            name='slug',
        ),
        migrations.AlterField(
            model_name='account',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='image',
            name='post',
            field=models.ManyToManyField(through='socialnet.PostImages', to='posts.post'),
        ),
        migrations.AlterField(
            model_name='postimages',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.post'),
        ),
        migrations.DeleteModel(
            name='Comments',
        ),
        migrations.DeleteModel(
            name='Post',
        ),
        migrations.DeleteModel(
            name='PostTags',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
        migrations.DeleteModel(
            name='Upvote',
        ),
    ]