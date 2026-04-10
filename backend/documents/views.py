"""
Django REST Framework views for document management.
"""

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Document, DocumentActivity
from .serializers import DocumentSerializer, DocumentActivitySerializer, PublicDocumentSerializer


def create_document_activity(document, action, message, changed_by=None, previous_status='', new_status=''):
    """Store a simple audit record for document activity."""
    DocumentActivity.objects.create(
        document=document,
        document_title=document.title,
        action=action,
        message=message,
        previous_status=previous_status,
        new_status=new_status,
        changed_by=getattr(changed_by, 'username', '') if changed_by else '',
    )


class DocumentActivityViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = DocumentActivitySerializer
    queryset = DocumentActivity.objects.select_related('document').all()

    def get_queryset(self):
        queryset = super().get_queryset()
        document_id = self.request.query_params.get('document_id')
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        return queryset


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing documents in open no-auth mode."""

    permission_classes = [AllowAny]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'doc_type', 'description', 'sender', 'receiver', 'owner', 'status', 'priority', 'remarks']
    ordering_fields = ['created_at', 'title', 'owner', 'due_date', 'status', 'priority']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PublicDocumentSerializer
        return DocumentSerializer

    def _get_access_key(self, request):
        key = request.headers.get('X-Document-Key') or request.query_params.get('access_key')
        if not key and hasattr(request, 'data'):
            if isinstance(request.data, dict):
                key = request.data.get('access_key')
            else:
                key = request.data.get('access_key', None)

        if isinstance(key, str):
            return key.strip()
        return key

    def _validate_document_access(self, request, document):
        access_key = self._get_access_key(request)
        if not access_key:
            return Response({'error': 'Document access key is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not document.check_access_key(access_key):
            return Response({'error': 'Invalid document access key.'}, status=status.HTTP_403_FORBIDDEN)

        return None

    def get_queryset(self):
        queryset = super().get_queryset()
        owner = self.request.query_params.get('owner')
        if owner:
            queryset = queryset.filter(owner__iexact=owner)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            previous_status = ''
            self.perform_create(serializer)
            document = serializer.instance
            create_document_activity(
                document,
                DocumentActivity.ACTION_CREATED,
                f'Document {document.document_number} was created.',
                request.user if getattr(request, 'user', None) else None,
                previous_status=previous_status,
                new_status=document.status,
            )
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as exc:
            return Response({'error': f'Failed to create document: {str(exc)}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_documents = Document.objects.count()
        owners = Document.objects.values('owner').distinct().count()
        recent_count = Document.objects.filter(created_at__gte=timezone.now().replace(day=1)).count()

        status_counts = {
            'pending': Document.objects.filter(status=Document.STATUS_PENDING).count(),
            'in_process': Document.objects.filter(status=Document.STATUS_IN_PROCESS).count(),
            'approved': Document.objects.filter(status=Document.STATUS_APPROVED).count(),
            'rejected': Document.objects.filter(status=Document.STATUS_REJECTED).count(),
            'completed': Document.objects.filter(status=Document.STATUS_COMPLETED).count(),
        }

        return Response({
            'total_documents': total_documents,
            'unique_owners': owners,
            'documents_this_month': recent_count,
            'status_counts': status_counts,
        })

    @action(detail=False, methods=['get'])
    def by_owner(self, request):
        owner = request.query_params.get('owner')
        if not owner:
            return Response({'error': 'owner query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        documents = self.get_queryset().filter(owner__iexact=owner)
        serializer = self.get_serializer(documents, many=True)
        return Response({'owner': owner, 'count': documents.count(), 'documents': serializer.data})

    @action(detail=False, methods=['get'])
    def resolve_qr(self, request):
        encrypted_id = request.query_params.get('encrypted_id')
        if not encrypted_id:
            return Response({'error': 'encrypted_id query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        document = Document.objects.filter(encrypted_id=encrypted_id).first()
        if not document:
            return Response({'error': 'Document not found for the provided QR code'}, status=status.HTTP_404_NOT_FOUND)

        access_error = self._validate_document_access(request, document)
        if access_error:
            return access_error

        create_document_activity(
            document,
            DocumentActivity.ACTION_LOOKED_UP,
            f'Document {document.document_number} was resolved from QR code.',
            request.user if getattr(request, 'user', None) else None,
            previous_status=document.status,
            new_status=document.status,
        )

        serializer = self.get_serializer(document)
        return Response({
            'document': serializer.data,
            'resolved_document_id': str(document.id),
            'resolved_document_number': document.document_number,
            'resolved_reference_code': document.reference_code,
        })

    def retrieve(self, request, *args, **kwargs):
        document = self.get_object()
        access_error = self._validate_document_access(request, document)
        if access_error:
            return access_error
        serializer = self.get_serializer(document)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        access_error = self._validate_document_access(request, instance)
        if access_error:
            return access_error

        previous_status = instance.status
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        create_document_activity(
            serializer.instance,
            DocumentActivity.ACTION_UPDATED,
            f'Document {serializer.instance.document_number} was updated.',
            request.user if getattr(request, 'user', None) else None,
            previous_status=previous_status,
            new_status=serializer.instance.status,
        )

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        access_error = self._validate_document_access(request, instance)
        if access_error:
            return access_error

        create_document_activity(
            instance,
            DocumentActivity.ACTION_DELETED,
            f'Document {instance.document_number} was deleted.',
            request.user if getattr(request, 'user', None) else None,
            previous_status=instance.status,
            new_status='Deleted',
        )
        return super().destroy(request, *args, **kwargs)
