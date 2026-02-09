from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tdm_orchestrator.models import Type, Entity, DataSource, Application, SqlScript, Runner, RunnerStep

class Command(BaseCommand):
    help = 'Crée des données de test pour TDM Orchestrator'

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('Aucun utilisateur trouvé. Créez un superuser d\'abord.'))
            return

        # Types
        type_oracle = Type.objects.create(value_format='SGDB', value_char='ORACLE', type_list='sgbd')
        type_postgres = Type.objects.create(value_format='SGDB', value_char='POSTGRES', type_list='sgbd')

        # Entity
        entity = Entity.objects.create(name='Entité Test', created_by=user)

        # DataSource
        ds = DataSource.objects.create(
            reference='DS1',
            name='DataSource Test',
            sgbd_name=type_oracle,
            sgbd_host='localhost',
            created_by=user
        )

        # Application
        app = Application.objects.create(
            reference='APP1',
            name='Application Test',
            type1=type_postgres,
            created_by=user
        )
        app.entity.add(entity)
        app.data_sources.add(ds)

        # SqlScript
        script1 = SqlScript.objects.create(
            name='Script Pre',
            description='Script de prétraitement',
            application=app,
            datasource=ds,
            script_type='PRE',
            content='SELECT 1;',
            created_by=user
        )
        script2 = SqlScript.objects.create(
            name='Script Post',
            description='Script de post-traitement',
            application=app,
            datasource=ds,
            script_type='POST',
            content='SELECT 2;',
            created_by=user
        )

        # Runner
        runner = Runner.objects.create(
            name='Runner Test',
            description='Orchestrateur de test',
            application=app,
            stop_on_error=True,
            verbose_logging=True,
            created_by=user
        )

        # RunnerStep
        RunnerStep.objects.create(runner=runner, script=script1, order=1, step_type='PRE')
        RunnerStep.objects.create(runner=runner, script=script2, order=1, step_type='POST')

        self.stdout.write(self.style.SUCCESS('Données de test créées avec succès.'))
