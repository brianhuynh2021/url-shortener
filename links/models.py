from django.db import models
from django.contrib.auth import get_user_model
import secrets

User = get_user_model()

class Link(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='links')
    title = models.CharField(max_length=200)
    target_url = models.URLField()
    slug = models.SlugField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.slug} -> {self.target_url}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self, length: int = 6) -> str:
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        while True:
            new_slug = ''.join(secrets.choice(chars) for _ in range(length))
            if not Link.objects.filter(slug=new_slug).exists():
                return new_slug

class Click(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='clicks')
    ts = models.DateTimeField(auto_now_add=True)
    referrer = models.CharField(max_length=255, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    ip_hash = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f'Click {self.id} - {self.link.slug} at {self.ts}'
