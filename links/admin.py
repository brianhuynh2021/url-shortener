from django.contrib import admin
from .models import Link, Click

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'title', 'owner', 'is_active', 'created_at')
    search_fields = ('slug', 'title', 'target_url', 'owner__username')
    list_filter = ('is_active', 'created_at')

@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ('id', 'link', 'ts', 'referrer')
    search_fields = ('link__slug', 'referrer', 'user_agent', 'ip_hash')
    list_filter = ('ts',)
