from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import Link, Click

@receiver(post_migrate)
def seed_demo_data(sender, **kwargs):
    if Link.objects.exists():
        return

    User = get_user_model()

    # admin/password123 (superuser)
    admin, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com"})
    admin.set_password("password123")
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()

    # hai/password123 (normal)
    hai, _ = User.objects.get_or_create(username="hai", defaults={"email": "hai@example.com"})
    hai.set_password("password123")
    hai.save()

    # sample links
    l1 = Link.objects.create(owner=hai, title="Google", target_url="https://www.google.com", slug="ggl")
    l2 = Link.objects.create(owner=hai, title="YouTube", target_url="https://www.youtube.com", slug="yt")
    l3 = Link.objects.create(owner=admin, title="UIT - Khoa CNTT", target_url="https://www.uit.edu.vn", slug="uit")
    l4 = Link.objects.create(owner=admin, title="Django REST Framework", target_url="https://www.django-rest-framework.org", slug="drf")

    now = timezone.now()
    for link, n in [(l1,8), (l2,15), (l3,5), (l4,11)]:
        for i in range(n):
            c = Click.objects.create(link=link, referrer="", user_agent="seed-bot", ip_hash="demo")
            from django.db.models import F
            Click.objects.filter(id=c.id).update(ts=now - timedelta(days=(i % 10)))
