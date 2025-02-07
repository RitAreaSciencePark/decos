# Generated by Django 5.1.6 on 2025-02-07 13:58

import PRP_CDM_app.models
import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PRP_CDM_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Administration',
            fields=[
                ('sr_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('lab_id', models.CharField(max_length=50)),
                ('dmptitle', models.CharField(blank=True, max_length=128)),
                ('user_id', models.CharField(max_length=50)),
                ('email', models.CharField(blank=True, max_length=128)),
                ('affiliation', models.CharField(blank=True, max_length=128)),
                ('experimentabstract', models.TextField(blank=True, max_length=500)),
            ],
            options={
                'db_table': 'administration',
            },
        ),
        migrations.CreateModel(
            name='API_Tokens',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('elab_token', models.CharField(blank=True, max_length=128, null=True)),
                ('jenkins_token', models.CharField(blank=True, max_length=128, null=True)),
            ],
            options={
                'db_table': 'api_tokens',
            },
        ),
        migrations.CreateModel(
            name='Instruments',
            fields=[
                ('instrument_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('vendor', models.CharField(max_length=50)),
                ('model', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'db_table': 'instruments',
            },
        ),
        migrations.CreateModel(
            name='InstrumentXTechnique',
            fields=[
                ('x_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('instrument_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.instruments')),
            ],
            options={
                'db_table': 'instrument_x_technique',
            },
        ),
        migrations.CreateModel(
            name='labDMP',
            fields=[
                ('lab_id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('user_id', models.CharField(max_length=50)),
                ('instrument_metadata_collection', models.CharField(blank=True, max_length=128)),
                ('additional_enotebook_open_collection', models.CharField(blank=True, max_length=128)),
                ('sample_standard', models.CharField(blank=True, max_length=128)),
                ('metadata_schema_defined', models.CharField(blank=True)),
                ('open_trusted_repo_published_data', models.BooleanField(blank=True)),
                ('open_data_licence', models.CharField(blank=True)),
                ('open_access_journal_publication', models.BooleanField(blank=True)),
                ('clear_data_provenance', models.BooleanField(blank=True)),
                ('related_data_open', models.BooleanField(blank=True)),
                ('licence_scientific_documents', models.BooleanField(blank=True)),
                ('raw_data_storage_location', models.CharField(blank=True)),
                ('raw_data_storage_time_retention', models.CharField(blank=True)),
                ('backup_policy_published_data', models.CharField(blank=True)),
                ('backup_policy_unplublished_data', models.CharField(blank=True)),
            ],
            options={
                'db_table': 'labdmp',
            },
        ),
        migrations.CreateModel(
            name='Laboratories',
            fields=[
                ('lab_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'laboratories',
            },
        ),
        migrations.CreateModel(
            name='LabXInstrument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instrument_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.instruments')),
                ('lab_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.laboratories')),
            ],
            options={
                'db_table': 'lab_x_instrument',
            },
        ),
        migrations.CreateModel(
            name='Samples',
            fields=[
                ('sample_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('sample_short_description', models.CharField(max_length=64)),
                ('sample_description', models.TextField(blank=True, max_length=500)),
                ('sample_feasibility', models.CharField(blank=True, choices=[('feasible', 'feasible'), ('not feasible', 'not feasible'), ('feasible with reservations', 'feasible with reservations')])),
                ('sample_status', models.CharField(default='Submitted')),
                ('sample_location', models.CharField(blank=True, null=True)),
                ('lab_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.laboratories')),
            ],
            options={
                'db_table': 'samples',
            },
        ),
        migrations.CreateModel(
            name='Proposals',
            fields=[
                ('proposal_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('proposal_status', models.CharField(default='Submitted')),
                ('proposal_feasibility', models.CharField(blank=True, choices=[('feasible', 'feasible'), ('not feasible', 'not feasible'), ('feasible with reservations', 'feasible with reservations')])),
                ('proposal_date', models.DateField(default=datetime.date.today)),
                ('proposal_filename', models.FileField(blank=True, upload_to=PRP_CDM_app.models.Proposals.user_directory_path)),
            ],
            options={
                'db_table': 'proposals',
            },
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('question_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('question', models.TextField(blank=True, max_length=500)),
                ('answer', models.TextField(blank=True, max_length=500)),
                ('sample_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.samples')),
            ],
            options={
                'db_table': 'questions',
            },
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('result_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('main_repository', models.CharField(blank=True, max_length=2048)),
                ('article_doi', models.CharField(blank=True, max_length=256)),
            ],
            options={
                'db_table': 'results',
            },
        ),
        migrations.CreateModel(
            name='ResultxInstrument',
            fields=[
                ('x_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('instruments', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.instruments')),
                ('results', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.results')),
            ],
            options={
                'db_table': 'result_x_instrument',
            },
        ),
        migrations.CreateModel(
            name='ResultxLab',
            fields=[
                ('x_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('lab', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.laboratories')),
                ('results', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.results')),
            ],
            options={
                'db_table': 'result_x_lab',
            },
        ),
        migrations.CreateModel(
            name='ResultxSample',
            fields=[
                ('x_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('results', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.results')),
                ('samples', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.samples')),
            ],
            options={
                'db_table': 'result_x_sample',
            },
        ),
        migrations.CreateModel(
            name='ServiceRequests',
            fields=[
                ('sr_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('sr_status', models.CharField(default='Submitted')),
                ('exp_description', models.TextField(blank=True, max_length=500)),
                ('output_delivery_date', models.DateField(blank=True)),
                ('lab_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.laboratories')),
                ('proposal_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.proposals')),
            ],
            options={
                'db_table': 'service_requests',
            },
        ),
        migrations.CreateModel(
            name='Steps',
            fields=[
                ('step_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('assigned_uoa', models.IntegerField()),
                ('performed_uoa', models.IntegerField(default=0)),
                ('eff_sample_date_of_delivery', models.DateField()),
                ('eff_reagents_date_of_delivery', models.DateField()),
                ('sample_quality', models.CharField(blank=True)),
                ('sample_quality_description', models.TextField(blank=True, max_length=500)),
                ('sample_quality_extra_budjet', models.BooleanField(blank=True)),
                ('instrument_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.instruments')),
            ],
            options={
                'db_table': 'steps',
            },
        ),
        migrations.CreateModel(
            name='Techniques',
            fields=[
                ('technique_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('technique_name', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'db_table': 'techniques',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('user_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name_surname', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=128)),
                ('affiliation', models.CharField(max_length=128)),
                ('gender', models.CharField(choices=[('male', 'male'), ('female', 'female'), ('other', 'other')])),
                ('legal_status', models.CharField(blank=True, choices=[('OTH', 'OTH'), ('PRV', 'PRV'), ('RES', 'RES'), ('SME', 'SME'), ('UNI', 'UNI')], null=True)),
                ('research_role', models.CharField(choices=[('senior scientist', 'senior scientist'), ('phd student', 'phd student'), ('professor / scientific coordinator', 'professor / scientific coordinator'), ('scientist', 'scientist'), ('manager', 'manager'), ('degree student', 'degree student'), ('post-doc', 'post-doc'), ('technician', 'technician'), ('other', 'other')])),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.DeleteModel(
            name='CustomAppModel',
        ),
        migrations.AddField(
            model_name='api_tokens',
            name='laboratory',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.laboratories'),
        ),
        migrations.CreateModel(
            name='LageSamples',
            fields=[
                ('samples_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='PRP_CDM_app.samples')),
                ('type', models.CharField(blank=True)),
                ('is_volume_in_ul', models.CharField(blank=True)),
                ('is_buffer_used', models.CharField(blank=True)),
                ('is_quality', models.CharField(blank=True)),
                ('sample_date_of_delivery', models.DateField()),
                ('sample_back', models.BooleanField()),
                ('reagents_provided_by_client', models.BooleanField()),
                ('reagents_date_of_delivery', models.DateField(blank=True, null=True)),
                ('sample_sheet_filename', models.FileField(blank=True, upload_to=PRP_CDM_app.models.LageSamples.user_directory_path)),
                ('additional_filename', models.FileField(blank=True, upload_to=PRP_CDM_app.models.LageSamples.user_directory_path)),
            ],
            options={
                'db_table': 'lage_samples',
            },
            bases=('PRP_CDM_app.samples',),
        ),
        migrations.CreateModel(
            name='LameSamples',
            fields=[
                ('samples_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='PRP_CDM_app.samples')),
                ('chemical_formula', models.CharField(blank=True)),
                ('elements_list', models.CharField(blank=True)),
                ('sample_date_of_delivery', models.DateField()),
                ('sample_back', models.BooleanField()),
                ('sample_sheet_filename', models.FileField(blank=True, upload_to=PRP_CDM_app.models.LameSamples.user_directory_path)),
                ('additional_filename', models.FileField(blank=True, upload_to=PRP_CDM_app.models.LameSamples.user_directory_path)),
            ],
            options={
                'db_table': 'lame_samples',
            },
            bases=('PRP_CDM_app.samples',),
        ),
        migrations.AddField(
            model_name='samples',
            name='sr_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.servicerequests'),
        ),
        migrations.AddField(
            model_name='steps',
            name='sample_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.samples'),
        ),
        migrations.AddField(
            model_name='steps',
            name='technique_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.techniques'),
        ),
        migrations.AddField(
            model_name='instrumentxtechnique',
            name='technique_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.techniques'),
        ),
        migrations.AddField(
            model_name='proposals',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.users'),
        ),
        migrations.AddField(
            model_name='api_tokens',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='PRP_CDM_app.users'),
        ),
    ]
