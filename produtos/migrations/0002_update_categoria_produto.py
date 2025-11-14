# Generated migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categoria',
            options={'ordering': ['-data_criacao'], 'verbose_name': 'Categoria', 'verbose_name_plural': 'Categorias'},
        ),
        migrations.AlterModelOptions(
            name='produto',
            options={'ordering': ['-data_criacao'], 'verbose_name': 'Produto', 'verbose_name_plural': 'Produtos'},
        ),
        migrations.AddField(
            model_name='categoria',
            name='data_atualizacao',
            field=models.DateTimeField(auto_now=True, verbose_name='Última Atualização'),
        ),
        migrations.AlterField(
            model_name='categoria',
            name='data_criacao',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação'),
        ),
        migrations.AlterField(
            model_name='categoria',
            name='nome',
            field=models.CharField(help_text='Nome da categoria (ex: CASTANHAS, TEMPEROS)', max_length=100, verbose_name='Nome da Categoria'),
        ),
    ]
