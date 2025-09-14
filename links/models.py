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
    # New relations (optional)
    # Set below classes further down; use string refs here to avoid reordering issues
    domain = models.ForeignKey('Domain', on_delete=models.SET_NULL, null=True, blank=True, related_name='links')
    campaign = models.ForeignKey('Campaign', on_delete=models.SET_NULL, null=True, blank=True, related_name='links')
    tags = models.ManyToManyField('Tag', blank=True, related_name='links')

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

# New simple taxonomy and grouping models to reach >=5 tables
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Campaign(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Domain(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='domains')
    name = models.CharField(max_length=255, unique=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'

    def __str__(self):
        return self.name
