"""
Django REST Framework serializers for documents
"""

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from .models import Document, DocumentActivity


class DocumentActivitySerializer(serializers.ModelSerializer):
    """Serializer for the document audit trail."""

    class Meta:
        model = DocumentActivity
        fields = [
            'id',
            'document_title',
            'action',
            'message',
            'previous_status',
            'new_status',
            'changed_by',
            'created_at',
        ]
        read_only_fields = fields


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""

    class Meta:
        model = Document
        fields = [
            'id',
            'document_number',
            'reference_code',
            'department',
            'title',
            'doc_type',
            'description',
            'sender',
            'receiver',
            'owner',
            'status',
            'priority',
            'due_date',
            'remarks',
            'attachment',
            'encrypted_id',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'document_number', 'reference_code', 'encrypted_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'owner': {'required': False}
        }

    def validate_title(self, value):
        """Validate title is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()

    def validate_owner(self, value):
        """Validate owner is not empty if provided"""
        if value is None or not value.strip():
            raise serializers.ValidationError("Owner cannot be empty")
        return value.strip()

    def validate_sender(self, value):
        if value is None or not value.strip():
            raise serializers.ValidationError('Sender cannot be empty')
        return value.strip()

    def validate_receiver(self, value):
        if value is None or not value.strip():
            raise serializers.ValidationError('Receiver cannot be empty')
        return value.strip()

    def create(self, validated_data):
        request = self.context.get('request')
        if not validated_data.get('owner') and request and request.user and not request.user.is_staff:
            validated_data['owner'] = request.user.username
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['activities'] = DocumentActivitySerializer(instance.activities.all(), many=True).data
        if instance.attachment and 'request' in self.context:
            request = self.context['request']
            representation['attachment'] = request.build_absolute_uri(instance.attachment.url)
        return representation


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django User accounts."""

    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'password']
        read_only_fields = ['id']
        extra_kwargs = {
            'email': {'required': False},
            'is_staff': {'required': False},
        }

    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Username cannot be empty')
        return value.strip()

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Password is required.'})

        user = User(
            username=validated_data.get('username'),
            email=validated_data.get('email', ''),
            is_staff=validated_data.get('is_staff', False),
        )
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Django auth groups."""

    class Meta:
        model = Group
        fields = ['id', 'name']


class TokenSerializer(serializers.ModelSerializer):
    """Serializer for DRF authentication tokens."""

    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Token
        fields = ['key', 'user_id', 'username', 'created']
        read_only_fields = ['key', 'created', 'user_id', 'username']
