from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('django_spire_metric_visual', '0006_visualregion')]

    operations = [migrations.RemoveField(model_name='visual', name='date')]
