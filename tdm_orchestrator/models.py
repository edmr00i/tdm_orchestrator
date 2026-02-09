

from django.db import models, connection
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

# Définition du manager après les imports
class TypeManager(models.Manager):
    pass

class Type(models.Model):
    reference = models.CharField(max_length=255, blank=True, null=True)
    value_format = models.CharField(max_length=50)
    value_char = models.CharField(max_length=255, blank=True, null=True)
    value_num = models.IntegerField(blank=True, null=True)
    value_date = models.DateTimeField(blank=True, null=True)
    type_list = models.CharField(max_length=255)
    source = models.CharField(max_length=30, default='client')
    lock = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(db_column="creation_date", auto_now_add=True)
    update_at = models.DateTimeField(db_column="modification_date", auto_now=True)
    extern_ref_admin_lov = models.BigIntegerField(blank=True, null=True, default=None)
    objects = TypeManager()

    def get_translated_field_value(self, field_name):
        value = self.__dict__[field_name]
        return value

    def find_by_value_char(self, value_char):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM yourapp_typetable
                WHERE value_char = %s AND is_active = %s AND is_deleted = %s
            """, [value_char, True, False])
            result = cursor.fetchall()
            types = []
            for row in result:
                types.append(self.__class__(*row))
            return types

    @property
    def value_char_translated(self):
        return self.get_translated_field_value('value_char')

    def __str__(self):
        return self.value_char or str(self.pk)

# Nouveau modèle Entity
class Entity(models.Model):
    reference = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=255)
    siret = models.CharField(max_length=255, null=True, blank=True)
    sigle = models.CharField(max_length=255, null=True, blank=True)
    dpo = models.CharField(max_length=255, null=True, blank=True)
    forme_juridique = models.ForeignKey(
        Type,
        related_name='forme_juridique',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    address_postal = models.CharField(max_length=255, null=True, blank=True)
    numero_dpo = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    type_entite = models.ForeignKey(
        Type,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        db_column="creation_date",
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        db_column="modification_date",
        auto_now=True
    )
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        null=True
    )
    def __str__(self):
        return self.name

# =====================
# DataSource et Application
# =====================
class DataSource(models.Model):
    reference = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    sgbd_name = models.ForeignKey(Type, related_name='sgbd', on_delete=models.PROTECT)
    sgbd_password = models.TextField(blank=True, null=True)
    priv_key = models.TextField(blank=True, null=True)
    sgbd_host = models.CharField(max_length=255)
    sgbd_user = models.CharField(max_length=255, null=True, blank=True)
    sgbd_port = models.IntegerField(null=True, blank=True)
    sgbd_driver = models.CharField(max_length=255, null=True, blank=True)
    sgbd_sid = models.CharField(max_length=255, null=True, blank=True)
    sgbd_database = models.CharField(max_length=255, null=True, blank=True)
    sgbd_tls = models.BooleanField(default=False)
    sgbd_x509 = models.BooleanField(default=False)
    sgbd_ca_file = models.TextField(blank=True, null=True)
    sgbd_certificate_key_file = models.TextField(blank=True, null=True)
    sgbd_certificate_file = models.TextField(blank=True, null=True)
    sgbd_certificate_key_file_password = models.CharField(max_length=256, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(db_column="creation_date", auto_now_add=True)
    updated_at = models.DateTimeField(db_column="modification_date", auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True)
    def __str__(self):
        return self.name

class Application(models.Model):
    reference = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    type1 = models.ForeignKey(Type, on_delete=models.PROTECT, blank=True, null=True)
    type2 = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(null=True)
    mac_address = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.CharField(max_length=255, blank=True, null=True)
    entity = models.ManyToManyField(Entity, related_name='application_entity')
    data_sources = models.ManyToManyField('DataSource', related_name='application_datasource', blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(db_column="creation_date", auto_now_add=True)
    updated_at = models.DateTimeField(db_column="modification_date", auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True)
    def __str__(self):
        return self.name

"""
Modèles Django pour le module TDM SQL Orchestrator
"""


from django.db import models, connection
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

# Définition du manager après les imports
class TypeManager(models.Manager):
    pass


# =============================================================================
# MODÈLE 1 : SCRIPT SQL
# =============================================================================
class SqlScript(models.Model):
    """
    Représente un script SQL unitaire qui peut être exécuté sur une base de données.
    
    Exemples d'usage :
    - Désactiver les contraintes avant anonymisation
    - Nettoyer les logs temporaires
    - Recréer les index après traitement
    """
    
    # Types de scripts disponibles
    SCRIPT_TYPES = [
        ('PRE', 'Pre-Processing'),      # Exécuté AVANT l'anonymisation
        ('POST', 'Post-Processing'),    # Exécuté APRÈS l'anonymisation
        ('UTIL', 'Utility'),            # Script utilitaire (usage libre)
    ]
    
    # Champs de base
    name = models.CharField(
        max_length=255,
        verbose_name="Nom du script",
        help_text="Ex: Disable_FK_CRM, Clean_Audit_Logs"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Explication de ce que fait le script"
    )
    
    # Relations avec d'autres entités
    # ForeignKey vers Application et DataSource (modèles externes)
    # Utilisation de settings pour permettre la configuration dynamique
    application = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name="Application cible", help_text="L'application concernée (CRM, ERP, etc.)")
    datasource = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Source de données", help_text="La connexion DB sur laquelle exécuter ce script")
    
    # Type et contenu du script
    script_type = models.CharField(
        max_length=10,
        choices=SCRIPT_TYPES,
        default='UTIL',
        verbose_name="Type de script"
    )
    
    content = models.TextField(
        verbose_name="Contenu SQL",
        help_text="Le code SQL brut. Supporte les variables comme ${TARGET_SCHEMA}"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    created_by = models.ForeignKey(
        'auth.User',  # Utilisateur Django standard
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_scripts',
        verbose_name="Créé par"
    )
    
    class Meta:
        verbose_name = "Script SQL"
        verbose_name_plural = "Scripts SQL"
        ordering = ['-created_at']  # Plus récents en premier
        indexes = [
            models.Index(fields=['script_type']),
            models.Index(fields=['application']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_script_type_display()})"
    
    def get_badge_color(self):
        """Retourne une couleur pour l'affichage dans l'UI"""
        colors = {
            'PRE': 'orange',
            'POST': 'purple',
            'UTIL': 'gray',
        }
        return colors.get(self.script_type, 'gray')
    
    def has_variables(self):
        """Vérifie si le script contient des variables à remplacer"""
        return '${' in self.content


# =============================================================================
# MODÈLE 2 : RUNNER (Orchestrateur)
# =============================================================================
class Runner(models.Model):
    """
    Représente un scénario d'exécution complet : un ensemble de scripts
    organisés en séquence Pre-Process → Anonymisation → Post-Process.
    
    Exemple : "Refresh Mensuel CRM"
    - Pre: Désactiver FK, nettoyer logs
    - Anonymisation (moteur TDM existant)
    - Post: Recréer index, activer FK
    """
    
    # Configuration de base
    name = models.CharField(
        max_length=255,
        verbose_name="Nom du Runner",
        help_text="Ex: Refresh Mensuel CRM, Purge Logs Hebdo"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Objectif de cet orchestrateur"
    )
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name="Application cible")
    
    # Stratégie d'exécution
    stop_on_error = models.BooleanField(
        default=True,
        verbose_name="Arrêter en cas d'erreur",
        help_text="Si True, arrête tout dès qu'un script échoue. Si False, continue (Best Effort)"
    )
    
    verbose_logging = models.BooleanField(
        default=False,
        verbose_name="Logs verbeux",
        help_text="Active les logs détaillés pour le débogage"
    )
    
    # Relation Many-to-Many avec les scripts (via table intermédiaire)
    scripts = models.ManyToManyField(
        SqlScript,
        through='RunnerStep',  # Table intermédiaire pour gérer l'ordre
        related_name='runners',
        verbose_name="Scripts associés"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_runners',
        verbose_name="Créé par"
    )
    
    class Meta:
        verbose_name = "Runner (Orchestrateur)"
        verbose_name_plural = "Runners (Orchestrateurs)"
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name
    
    def get_pre_scripts(self):
        """Récupère tous les scripts de pré-traitement dans l'ordre"""
        return self.runnerstep_set.filter(step_type='PRE').select_related('script')
    
    def get_post_scripts(self):
        """Récupère tous les scripts de post-traitement dans l'ordre"""
        return self.runnerstep_set.filter(step_type='POST').select_related('script')
    
    def total_scripts_count(self):
        """Nombre total de scripts dans ce runner"""
        return self.runnerstep_set.count()


# =============================================================================
# MODÈLE 3 : RUNNER STEP (Table intermédiaire)
# =============================================================================
class RunnerStep(models.Model):
    """
    Table intermédiaire qui lie un Runner à ses Scripts avec un ordre d'exécution.
    
    Permet de dire : "Dans le Runner X, exécuter le Script Y en position 2 du Pre-Process"
    """
    
    STEP_TYPES = [
        ('PRE', 'Pre-Process'),
        ('POST', 'Post-Process'),
    ]
    
    # Relations
    runner = models.ForeignKey(
        Runner,
        on_delete=models.CASCADE,
        verbose_name="Runner"
    )
    
    script = models.ForeignKey(
        SqlScript,
        on_delete=models.CASCADE,
        verbose_name="Script"
    )
    
    # Position dans la séquence
    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Ordre d'exécution",
        help_text="Position dans la séquence (1, 2, 3...)"
    )
    
    # Phase d'exécution
    step_type = models.CharField(
        max_length=10,
        choices=STEP_TYPES,
        verbose_name="Phase",
        help_text="Pre-Process ou Post-Process"
    )
    
    # Configuration optionnelle par étape
    enabled = models.BooleanField(
        default=True,
        verbose_name="Activé",
        help_text="Permet de désactiver temporairement un script sans le supprimer"
    )
    
    timeout_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Timeout (secondes)",
        help_text="Durée max d'exécution pour ce script spécifiquement"
    )
    
    class Meta:
        verbose_name = "Étape de Runner"
        verbose_name_plural = "Étapes de Runner"
        ordering = ['step_type', 'order']  # Trier par phase puis par ordre
        unique_together = [
            ('runner', 'script', 'step_type'),  # Un script ne peut être qu'une fois dans une phase
        ]
        indexes = [
            models.Index(fields=['runner', 'step_type', 'order']),
        ]
    
    def __str__(self):
        return f"{self.runner.name} → {self.step_type} #{self.order}: {self.script.name}"



# Historique des exécutions (version simplifiée)
class ExecutionLog(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('RUNNING', 'En cours'),
        ('SUCCESS', 'Succès'),
        ('FAILURE', 'Échec'),
    ]
    runner = models.ForeignKey(Runner, on_delete=models.CASCADE, null=True, blank=True, related_name='executions')
    script = models.ForeignKey(SqlScript, on_delete=models.CASCADE, null=True, blank=True, related_name='executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    logs = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    def __str__(self):
        if self.runner:
            return f"[{self.status}] {self.runner.name} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"
        elif self.script:
            return f"[{self.status}] {self.script.name} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"
        return f"Log #{self.id}"

