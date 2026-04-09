"""
Django admin configuration for documents
"""

from django.contrib import admin
from rest_framework.authtoken.models import Token
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'encrypted_id', 'created_at']
    search_fields = ['title', 'owner', 'encrypted_id']
    readonly_fields = ['id', 'encrypted_id', 'created_at', 'updated_at']
    list_filter = ['created_at', 'owner']


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['key', 'user', 'created']
    search_fields = ['key', 'user__username']
    readonly_fields = ['key', 'created']
    list_filter = ['created']
