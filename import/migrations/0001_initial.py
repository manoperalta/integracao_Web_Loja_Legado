# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FTPConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(default='Servidor FTP Principal', max_length=100, verbose_name='Nome da Configuração')),
                ('host', models.CharField(help_text='Endereço do servidor FTP (ex: ftp.exemplo.com.br)', max_length=255, verbose_name='Host FTP')),
                ('porta', models.IntegerField(default=21, help_text='Porta do servidor FTP (padrão: 21)', verbose_name='Porta')),
                ('usuario', models.CharField(help_text='Nome de usuário para autenticação FTP', max_length=100, verbose_name='Usuário')),
                ('senha', models.CharField(help_text='Senha para autenticação FTP', max_length=255, verbose_name='Senha')),
                ('diretorio', models.CharField(blank=True, help_text='Diretório/pasta no servidor FTP onde estão os arquivos (ex: 1)', max_length=255, verbose_name='Diretório')),
                ('ativo', models.BooleanField(default=True, help_text='Apenas uma configuração pode estar ativa por vez', verbose_name='Ativo')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Última Atualização')),
            ],
            options={
                'verbose_name': 'Configuração FTP',
                'verbose_name_plural': 'Configurações FTP',
                'ordering': ['-ativo', '-data_atualizacao'],
            },
        ),
    ]
