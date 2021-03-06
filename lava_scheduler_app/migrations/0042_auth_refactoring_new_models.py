# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-03 09:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0008_alter_user_username_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("lava_scheduler_app", "0041_notification_charfield_to_textfield"),
    ]

    operations = [
        migrations.CreateModel(
            name="GroupObjectPermission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "object_id",
                    models.CharField(max_length=255, verbose_name="object ID"),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.ContentType",
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="auth.Group"
                    ),
                ),
                (
                    "permission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auth.Permission",
                    ),
                ),
            ],
        ),
        migrations.AlterModelOptions(
            name="device",
            options={
                "permissions": (
                    ("view_device", "Can view device"),
                    ("submit_to_device", "Can submit jobs to device"),
                    ("admin_device", "Can admin device"),
                )
            },
        ),
        migrations.AlterModelOptions(
            name="devicetype",
            options={
                "permissions": (
                    ("view_devicetype", "Can view device type"),
                    ("submit_to_devicetype", "Can submit jobs to device type"),
                    ("admin_devicetype", "Can admin device type"),
                )
            },
        ),
        migrations.AlterModelOptions(
            name="testjob",
            options={
                "permissions": (
                    ("view_testjob", "Can view device type"),
                    ("admin_testjob", "Can admin test job"),
                    ("submit_testjob", "Can submit test job"),
                    ("cancel_resubmit_testjob", "Can cancel/resubmit job"),
                )
            },
        ),
        migrations.AlterUniqueTogether(
            name="groupobjectpermission",
            unique_together=set([("group", "permission", "content_type", "object_id")]),
        ),
    ]
