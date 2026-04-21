"""
Django admin configuration for documents
"""

from django.contrib import admin
from rest_framework.authtoken.models import Token
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'encrypted_id', 'access_key', 'created_at']
    search_fields = ['title', 'owner', 'encrypted_id', 'access_key']
    readonly_fields = ['id', 'encrypted_id', 'access_key', 'access_key_hash', 'created_at', 'updated_at']
    list_filter = ['created_at', 'owner']
    fieldsets = (
        (None, {
            'fields': (
                'id',
                'title',
                'owner',
                'department',
                'doc_type',
                'status',
                'priority',
                'document_number',
                'reference_code',
                'encrypted_id',
                'access_key',
                'access_key_hash',
            )
        }),
        ('Details', {
            'fields': (
                'description',
                'sender',
                'receiver',
                'due_date',
                'remarks',
                'attachment',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['key', 'user', 'created']
    search_fields = ['key', 'user__username']
    readonly_fields = ['key', 'created']
    list_filter = ['created']
