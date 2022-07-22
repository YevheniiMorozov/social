# Generated by Django 4.0.5 on 2022-07-22 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_alter_tag_name'),
        ('socialnet', '0014_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='history',
            name='follow',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='follow_user', to='socialnet.following'),
        ),
        migrations.AlterField(
            model_name='history',
            name='upvote_photo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upvote_photo', to='socialnet.upvotephoto'),
        ),
        migrations.AlterField(
            model_name='history',
            name='upvote_post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upvote_post', to='posts.upvote'),
        ),
    ]