# Generated by Django 4.2.5 on 2023-09-19 02:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bookapp", "0006_bookcomment_delete_bookcomments"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bookcomment",
            old_name="book_id",
            new_name="ebook_id",
        ),
    ]
