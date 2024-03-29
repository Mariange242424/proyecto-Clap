# Generated by Django 4.2.7 on 2023-11-23 00:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aplicacion', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='familia',
            name='jefe_de_familia',
        ),
        migrations.RemoveField(
            model_name='pagos',
            name='banco_emisor',
        ),
        migrations.RemoveField(
            model_name='pagos',
            name='banco_receptor',
        ),
        migrations.RemoveField(
            model_name='pagos',
            name='jefe_de_familia',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='familia_r',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='nivel_educ',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='num_bloque',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='num_calle',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='profesion',
        ),
        migrations.DeleteModel(
            name='Banco',
        ),
        migrations.DeleteModel(
            name='Bloque',
        ),
        migrations.DeleteModel(
            name='Calle',
        ),
        migrations.DeleteModel(
            name='Familia',
        ),
        migrations.DeleteModel(
            name='Nivel_Educ',
        ),
        migrations.DeleteModel(
            name='Pagos',
        ),
        migrations.DeleteModel(
            name='Persona',
        ),
        migrations.DeleteModel(
            name='Profesion',
        ),
    ]
