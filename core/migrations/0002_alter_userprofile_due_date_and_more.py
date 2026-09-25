from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="due_date",
            field=models.DateField(
                blank=True, help_text="Expected due date of delivery", null=True
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="emergency_contact_email",
            field=models.EmailField(
                blank=True,
                help_text="Email for emergency notifications",
                max_length=254,
                null=True,
            ),
        ),
    ]
