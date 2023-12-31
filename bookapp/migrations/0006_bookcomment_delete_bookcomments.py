# Generated by Django 4.2.5 on 2023-09-19 02:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bookapp", "0005_rename_bookcomment_bookcomments_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BookComment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("reader", models.CharField(max_length=255)),
                ("star", models.CharField(max_length=255)),
                ("time", models.CharField(max_length=255)),
                ("short_comm", models.TextField()),
                ("read_img", models.CharField(max_length=255)),
                ("book_img", models.CharField(max_length=255)),
                (
                    "book_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bookapp.ebook"
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="BookComments",
        ),
    ]
