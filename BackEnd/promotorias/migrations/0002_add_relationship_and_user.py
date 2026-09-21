from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('promotorias', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_usuario', models.CharField(max_length=100)),
                ('email_usuario', models.EmailField(max_length=254, unique=True)),
                ('senha_usuario', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PromotoriaResolucao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('promotoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='promotorias.promotoria')),
                ('resolucao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='promotorias.resolucao')),
            ],
        ),
    ]