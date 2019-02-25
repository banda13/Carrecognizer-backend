# Generated by Django 2.1.7 on 2019-02-23 16:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('make', models.CharField(max_length=50)),
                ('model', models.CharField(max_length=50)),
                ('accuracy', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Classification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('note', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClassificationFeedback',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('rate', models.IntegerField()),
                ('comment', models.CharField(max_length=255)),
                ('classification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Classification')),
            ],
        ),
        migrations.CreateModel(
            name='ClassificationResult',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('classification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Classification')),
            ],
        ),
        migrations.CreateModel(
            name='Classifier',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField()),
                ('active_from', models.DateTimeField()),
                ('active_to', models.DateTimeField()),
                ('accuracy', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='ImageFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('file_name', models.CharField(max_length=255)),
                ('file_path', models.CharField(max_length=255)),
                ('is_deleted', models.BooleanField()),
                ('file_size', models.IntegerField()),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('mime_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ClassificationResultCar',
            fields=[
                ('car_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Car')),
                ('classification_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ClassificationResult')),
            ],
            bases=('core.car',),
        ),
        migrations.CreateModel(
            name='ClassifierCar',
            fields=[
                ('car_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Car')),
                ('classifier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Classifier')),
            ],
            bases=('core.car',),
        ),
        migrations.AddField(
            model_name='classification',
            name='classifier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Classifier'),
        ),
        migrations.AddField(
            model_name='classification',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='classification',
            name='image',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.ImageFile'),
        ),
    ]
