from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations

def create_admin(apps, schema_editor):
    # Retrieve the auth API's user model dynamically to maintain safety
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    
    # Check if a user with the username 'admin' already exists
    if not User.objects.filter(username='admin').exists():
        admin_user = User(
            username='admin',
            email='admin@example.com',
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )
        # Encrypt the password correctly using Django's hasher
        admin_user.password = make_password('admin')
        admin_user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0005_document_access_key'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]