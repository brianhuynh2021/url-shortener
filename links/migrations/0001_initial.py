from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('target_url', models.URLField()),
                ('slug', models.SlugField(max_length=10, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Click',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts', models.DateTimeField(auto_now_add=True)),
                ('referrer', models.CharField(blank=True, max_length=255)),
                ('user_agent', models.CharField(blank=True, max_length=255)),
                ('ip_hash', models.CharField(blank=True, max_length=64)),
                ('link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clicks', to='links.link')),
            ],
        ),
    ]
