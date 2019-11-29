# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-11-29 12:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SKUSpecification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': 'SKU规格',
                'verbose_name_plural': 'SKU规格',
                'db_table': 'tb_sku_specification',
            },
        ),
        migrations.CreateModel(
            name='SpecificationOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('value', models.CharField(max_length=20, verbose_name='选项值')),
            ],
            options={
                'verbose_name': '规格选项',
                'verbose_name_plural': '规格选项',
                'db_table': 'tb_specification_option',
            },
        ),
        migrations.CreateModel(
            name='SPUSpecification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(max_length=20, verbose_name='规格名称')),
                ('spu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specs', to='goods.SPU', verbose_name='商品SPU')),
            ],
            options={
                'verbose_name': '商品SPU规格',
                'verbose_name_plural': '商品SPU规格',
                'db_table': 'tb_spu_specification',
            },
        ),
        migrations.AddField(
            model_name='specificationoption',
            name='spec',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='goods.SPUSpecification', verbose_name='规格'),
        ),
        migrations.AddField(
            model_name='skuspecification',
            name='option',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='goods.SpecificationOption', verbose_name='规格值'),
        ),
        migrations.AddField(
            model_name='skuspecification',
            name='sku',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specs', to='goods.SKU', verbose_name='sku'),
        ),
        migrations.AddField(
            model_name='skuspecification',
            name='spec',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='goods.SPUSpecification', verbose_name='规格名称'),
        ),
    ]