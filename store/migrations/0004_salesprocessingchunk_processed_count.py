from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_remove_salesprocessingchunk_end_order_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesprocessingchunk',
            name='processed_count',
            field=models.IntegerField(default=0),
        ),
    ]
