"""
Django REST Framework views for document management
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.conf import settings
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Document, DocumentActivity
from .serializers import DocumentSerializer, UserSerializer, GroupSerializer, TokenSerializer, DocumentActivitySerializer


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


class AuthLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'detail': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(
                {'detail': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'is_staff': user.is_staff,
        })


class AuthRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'detail': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'detail': 'Username already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'username': user.username,
            'is_staff': user.is_staff,
        }, status=status.HTTP_201_CREATED)


class AuthLogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'detail': 'Logged out successfully.'})


class AuthStatusView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'username': request.user.username,
            'is_staff': request.user.is_staff,
        })


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = User.objects.filter(is_superuser=False).order_by('username')
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class GroupViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer


class TokenViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Token.objects.select_related('user').all().order_by('user__username')
    serializer_class = TokenSerializer


class DocumentActivityViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentActivitySerializer

    def get_queryset(self):
        queryset = DocumentActivity.objects.select_related('document').all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(document__owner__iexact=self.request.user.username)
        document_id = self.request.query_params.get('document_id')
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        return queryset


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing documents with encryption

    Endpoints:
    - GET /api/documents/ - List documents
    - POST /api/documents/ - Create a new document
    - GET /api/documents/{id}/ - Retrieve document details
    - PUT /api/documents/{id}/ - Update document
    - DELETE /api/documents/{id}/ - Delete document
    - GET /api/documents/stats/ - Get statistics
    - GET /api/documents/by_owner/?owner=... - Filter documents by owner
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'doc_type', 'description', 'sender', 'receiver', 'owner', 'status', 'priority', 'remarks']
    ordering_fields = ['created_at', 'title', 'owner', 'due_date', 'status', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner__iexact=self.request.user.username)

        owner = self.request.query_params.get('owner')
        if owner:
            queryset = queryset.filter(owner__iexact=owner)

        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save()
        else:
            serializer.save(owner=self.request.user.username)

    def perform_update(self, serializer):
        if self.request.user.is_staff:
            serializer.save()
        else:
            serializer.save(owner=self.request.user.username)

    def create(self, request, *args, **kwargs):
        """Create a new document with automatic encryption"""
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
                request.user,
                previous_status=previous_status,
                new_status=document.status,
            )
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create document: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get document statistics"""
        if request.user.is_staff:
            total_documents = Document.objects.count()
            owners = Document.objects.values('owner').distinct().count()
            recent_count = Document.objects.filter(
                created_at__gte=timezone.now().replace(day=1)
            ).count()
        else:
            total_documents = Document.objects.filter(owner__iexact=request.user.username).count()
            owners = 1
            recent_count = Document.objects.filter(
                owner__iexact=request.user.username,
                created_at__gte=timezone.now().replace(day=1)
            ).count()

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
        """Get documents filtered by owner"""
        owner = request.query_params.get('owner')
        if not owner:
            return Response(
                {'error': 'owner query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        documents = self.get_queryset().filter(owner__iexact=owner)
        serializer = self.get_serializer(documents, many=True)
        return Response({
            'owner': owner,
            'count': documents.count(),
            'documents': serializer.data
        })

    @action(detail=False, methods=['get'])
    def resolve_qr(self, request):
        """Resolve a QR code payload back into the stored document."""
        encrypted_id = request.query_params.get('encrypted_id')
        if not encrypted_id:
            return Response(
                {'error': 'encrypted_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        document = Document.objects.filter(encrypted_id=encrypted_id).first()
        if not document:
            return Response(
                {'error': 'Document not found for the provided QR code'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not request.user.is_staff and document.owner.lower() != request.user.username.lower():
            return Response(
                {'error': 'You are not allowed to access this document.'},
                status=status.HTTP_403_FORBIDDEN
            )

        create_document_activity(
            document,
            DocumentActivity.ACTION_LOOKED_UP,
            f'Document {document.document_number} was resolved from QR code.',
            request.user,
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

    @action(detail=False, methods=['get'])
    def resolve_qr_token(self, request):
        """Resolve a signed QR token into a document with permission checks."""
        qr_token = request.query_params.get('token')
        if not qr_token:
            return Response(
                {'error': 'token query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        signer = signing.TimestampSigner(salt='documents.qr')
        token_max_age = getattr(settings, 'QR_TOKEN_MAX_AGE', None)

        try:
            if token_max_age:
                encrypted_id = signer.unsign(qr_token, max_age=token_max_age)
            else:
                encrypted_id = signer.unsign(qr_token)
        except SignatureExpired:
            return Response(
                {'error': 'QR token has expired.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except BadSignature:
            return Response(
                {'error': 'Invalid QR token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        document = Document.objects.filter(encrypted_id=encrypted_id).first()
        if not document:
            return Response(
                {'error': 'Document not found for the provided QR token'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not request.user.is_staff and document.owner.lower() != request.user.username.lower():
            return Response(
                {'error': 'You are not allowed to access this document.'},
                status=status.HTTP_403_FORBIDDEN
            )

        create_document_activity(
            document,
            DocumentActivity.ACTION_LOOKED_UP,
            f'Document {document.document_number} was resolved from signed QR token.',
            request.user,
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

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def admin_dashboard(self, request):
        """Admin-only dashboard summary"""
        total_documents = Document.objects.count()
        owners = Document.objects.values('owner').distinct().count()
        recent_count = Document.objects.filter(
            created_at__gte=timezone.now().replace(day=1)
        ).count()

        return Response({
            'total_documents': total_documents,
            'unique_owners': owners,
            'documents_this_month': recent_count,
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        previous_status = instance.status
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        create_document_activity(
            serializer.instance,
            DocumentActivity.ACTION_UPDATED,
            f'Document {serializer.instance.document_number} was updated.',
            request.user,
            previous_status=previous_status,
            new_status=serializer.instance.status,
        )

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        create_document_activity(
            instance,
            DocumentActivity.ACTION_DELETED,
            f'Document {instance.document_number} was deleted.',
            request.user,
            previous_status=instance.status,
            new_status='Deleted',
        )
        return super().destroy(request, *args, **kwargs)
