from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("chatbot", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS chatbot_document_embedding_idx "
            "ON chatbot_document USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);"
        ),
    ]
