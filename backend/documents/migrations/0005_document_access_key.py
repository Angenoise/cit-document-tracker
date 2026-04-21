from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_document_access_key_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='access_key',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
