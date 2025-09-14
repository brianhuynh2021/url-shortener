from django.contrib import admin
from .models import Link, Click, Tag, Campaign, Domain

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'title', 'owner', 'campaign', 'domain', 'is_active', 'created_at')
    search_fields = ('slug', 'title', 'target_url', 'owner__username')
    list_filter = ('is_active', 'created_at', 'campaign', 'domain')
    filter_horizontal = ('tags',)

@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ('id', 'link', 'ts', 'referrer')
    search_fields = ('link__slug', 'referrer', 'user_agent', 'ip_hash')
    list_filter = ('ts',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'name')

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'start_date', 'end_date', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('start_date', 'end_date', 'created_at')

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'verified', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('verified', 'created_at')
