from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_document_attachment_document_department_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='access_key_hash',
            field=models.CharField(blank=True, default='', max_length=128),
        ),
    ]
