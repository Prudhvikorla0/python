"""Models of the app Tenant."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from base.models import AbstractBaseModel
from utilities.url_utils import URL

from v1.blockchain.models.create_topic import AbstractTopic

from v1.tenants import constants as tenant_consts
from v1.accounts import constants as user_consts

from v1.dashboard import models as dashboard_models

from v1.bulk_templates import constants as bulk_const
from v1.bulk_templates import models as bulk_models

from v1.risk import models as risk_models
from v1.risk import constants as risk_consts

from v1.consumer_interface import models as ci_models


class Tenant(AbstractBaseModel, AbstractTopic):
    """
    Tenant it referred to the Company which will be implementing the 
    traceability system.

    Attribs:
        name(char)          : Name of the tenant company.
        subdiomain(char)    : Subdomain underwhich the tenant will be able to access
                              the platform
        

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    name = models.CharField(
        max_length=1000, default='', null=True, blank=True, 
        verbose_name=_('Tenant Name'))
    subdomain = models.CharField(
        max_length=32, verbose_name=_("Tenant subdomain"), unique=True)
    countries = models.ManyToManyField(
        'tenants.Country', related_name='tenants',
        verbose_name=_('Country List'))
    node_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, null=True, 
        blank=True, verbose_name=_('Extra Fields For Node'), 
        related_name='node_tenant')
    node_member_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, null=True, 
        blank=True, verbose_name=_('Extra Fields For Node Member'), 
        related_name='node_member_tenant')
    internal_transaction_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, null=True, 
        blank=True, verbose_name=_('Extra Fields For Internal Transaction'), 
        related_name='internal_transaction_tenant')
    external_transaction_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, null=True, 
        blank=True, verbose_name=_('Extra Fields For External Transaction'), 
        related_name='external_transaction_tenant')
    claim_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, null=True, 
        blank=True, verbose_name=_('Extra Fields For Claim'), 
        related_name='claim_tenant')
    txn_enquiry_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, null=True, 
        blank=True, verbose_name=_('Extra Fields For Transaction Enquiry'), 
        related_name='txn_enquiry_tenant')
    env_data_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, null=True, 
        blank=True, verbose_name=_('Environment Data Form'), 
        related_name='env_form_tenant')
    soc_data_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, null=True, 
        blank=True, verbose_name=_('Social Data Form'), 
        related_name='soc_form_tenant')
    gov_data_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, null=True, 
        blank=True, verbose_name=_('Governance Data Form'), 
        related_name='gov_form_tenant')
    
    currencies = models.ManyToManyField(
        'tenants.Currency', related_name='tenants',
        verbose_name=_('Currencies'))
    units = models.ManyToManyField(
        'products.Unit', related_name='tenants',
        verbose_name=_('Units'))

    # Configuration
    symmetrical_connection = models.BooleanField(default=True)
    connection_auto_approval = models.BooleanField(default=True)
    connection_disabling = models.BooleanField(default=False)
    transaction_auto_approval = models.BooleanField(default=True)
    transaction_rejection = models.BooleanField(default=True)
    mandatory_transaction_claims = models.BooleanField(default=False)

    ci_availability = models.IntegerField(
        default=tenant_consts.CIAvailability.TENANT_LEVEL,
        choices=tenant_consts.CIAvailability.choices,
        verbose_name=_('Node Anonymity'))
    node_anonymity = models.IntegerField(
        default=tenant_consts.NodeAnonymityType.FULLY_VISIBLE,
        choices=tenant_consts.NodeAnonymityType.choices,
        verbose_name=_('Node Anonymity'))
    node_discoverability = models.IntegerField(
        default=tenant_consts.DiscoverabilityType.HIDDEN,
        choices=tenant_consts.DiscoverabilityType.choices,
        verbose_name=_('Node Discoverability'))
    node_data_transparency = models.IntegerField(
        default=tenant_consts.NodeDataTransparency.FULLY_TRANSPARENT,
        choices=tenant_consts.NodeDataTransparency.choices,
        verbose_name=_('Node Data Transparency'))
    bulk_upload = models.BooleanField(
        default=False, verbose_name=_('Bulk Upload Enabled'))
    custom_excel_template = models.BooleanField(
        default=False, verbose_name=_('Is Tenant Customized Excel Enabled'))
    dynamic_fields = models.BooleanField(
        default=False, verbose_name=_('Dynamic Fields Enabled'))

    dashboard_theming = models.BooleanField(
        default=False, verbose_name=_('Is Dashboard Theming Enabled'))
    ci_theming = models.BooleanField(
        default=False, verbose_name=_('Is Consumer Interface Theming Enabled'))

    blockchain_logging = models.BooleanField(
        default=False, verbose_name=_('Is Blockchain Enabled'))

    transaction = models.BooleanField(
        default=True, verbose_name=_('Is Transaction Enabled'))
    claim = models.BooleanField(
        default=True, verbose_name=_('Is Claim Enabled'))
    node_claim = models.BooleanField(
        default=True, verbose_name=_('Is Company Claim Enabled'))
    batch_claim = models.BooleanField(
        default=True, verbose_name=_('Is Batch Claim Enabled'))
    connection_claim = models.BooleanField(
        default=True, verbose_name=_('Is Connection Claim Enabled'))
    purchase_order = models.BooleanField(
        default=True, verbose_name=_('Is Purchase Order Enabled'))
    risk_analysis = models.BooleanField(
        default=True, verbose_name=_('Is Risk Analysis Enabled'))
    show_empty_batches = models.BooleanField(
        default=True, verbose_name=_('Show empty batches Tab'))
    questionnaire = models.BooleanField(
        default=False, verbose_name=_('Is Questionnaire Enabled'))

    mobile_app = models.BooleanField(
        default=False, verbose_name=_('Is Mobile App Enabled'))

    topic_id = models.CharField(
        max_length=16, null=True, blank=True, default=settings.HUB_TOPIC_ID,
        verbose_name=_('Hedera Topic ID'))
    
    non_producer_stock_creation = models.BooleanField(
        default=False, verbose_name=_("Non Producer can create stock"))
    product_grouping = models.BooleanField(
        default=False, verbose_name=_("Is Product Grouping Enabled"))

    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.name} - {self.idencode}'

    def save(self, *args, **kwargs):
        """
        Checks can create multiple tenants and also makes force logout
        for all users under the specific tentant.
        """
        if not self.id and settings.ENTERPRISE_MODE:
            if Tenant.objects.count() > 0:
                raise ValueError(
                    _("Cannot have more than one tenant in Enterprise mode"))
        if not self.id:
            super(Tenant, self).save(*args, **kwargs)
            self.set_default_themes()
            self.create_ci_sections()
        else:
            self.users.update(force_logout=True)
            super(Tenant, self).save(*args, **kwargs)

    def create_ci_sections(self):
        """
        Create ci sections for the current tenant from a default 
        tenantsectionregistration added with none tenant.
        Everytime new default section added , we should update the 
        tenantsectionregistration model with that section none tenant.
        """
        default_sections = ci_models.SectionTenantRegister.objects.filter(
            tenant=None)
        for default_section in default_sections:
            section = default_section.section
            section.id = None
            section.save()
            default_section.id = None
            default_section.tenant = self
            default_section.section_object_id = section.id
            default_section.save()
        return True

    def set_default_ci_theme(self):
        """
        Method used to create ci themes for the current tenant
        from the default theme object values.
        """
        default_theme = ci_models.CITheme.objects.filter(
            is_default=True).first()
        default_theme.id = None
        default_theme.tenant = self
        default_theme.is_default = False
        default_theme.save()
        return True

    def set_default_themes(self):
        """
        Method to add default dhashboard theme for tenant.
        """
        from v1.dashboard import theme_colors
        from v1.dashboard.models import DashboardTheme, TrackerTheme
        
        dashboard_theme_data = theme_colors.dashboard_default_theme
        dashboard_theme_data['tenant'] = self
        tracker_theme_data = theme_colors.tracker_default_theme
        tracker_theme_data['tenant'] = self
        dashboard_theme = DashboardTheme(**dashboard_theme_data)
        tracker_theme = TrackerTheme(**tracker_theme_data)
        dashboard_theme.save()
        tracker_theme.save()
        self.set_default_ci_theme()
        return True

    def get_base_url(self):
        """
        Return root url of the tenant.
        """
        return URL(settings.FRONT_ROOT_URL.replace('tenant_custom_domain', self.subdomain))

    def get_tracker_url(self):
        """
        Return root url for the tracker of the tenant.
        """
        url = settings.TRACKER_ROOT_URL.replace('tenant_custom_domain', self.subdomain)
        return url

    def dashboard_theme(self):
        """Return dashboard theme."""
        try:
            if self.dashboard_theming and self.dashboard_theme:
                theme = self.dashboard_theme
            else:
                theme = dashboard_models.DashboardTheme.objects.filter(
                    is_default=True).first()
            return theme
        except:
            return None

    def tracker_theme(self, supply_chain=None):
        """Return tracker theme."""
        try:
            if self.ci_theming and self.tracker_themes and supply_chain:
                theme = self.tracker_themes.get(supply_chains=supply_chain)
            else:
                theme = dashboard_models.TrackerTheme.objects.filter(
                    is_default=True).first()
            return theme
        except:
            return None
        
    def ci_theme(self):
        """Return ci theme."""
        try:
            if self.ci_theming and self.ci_themes.all().exists():
                ci_theme = self.ci_themes.filter(
                    is_current=True).order_by('-id').first()
            else:
                ci_theme = ci_models.CITheme.objects.filter(
                    is_default=True).order_by('-id').first()
            return ci_theme
        except:
            return None

    @property
    def topic_name(self):
        """ To be implemented in the subclass to return name """
        return self.name

    def update_topic_id(self, bc_hash):
        """ To be implemented in the subclass to update hash when callback is received """
        self.topic_id = bc_hash['topicId']
        self.save()
        return True
    
    def connection_template(self):
        """
        Return default connection template of tenant if present or else returns 
        connection template under the tenant(non-default) and if its not 
        present it will return common connection template else return None
        """

        default_template = bulk_models.Template.objects.filter(
            is_default=True, tenant=self, 
            type=bulk_const.TemplateType.CONNECTION).first()
        if default_template:
            return default_template
        template = bulk_models.Template.objects.filter(
            tenant=self, type=bulk_const.TemplateType.CONNECTION).first()
        if template:
            return template
        common_template = bulk_models.Template.objects.filter(
            tenant=None, type=bulk_const.TemplateType.CONNECTION).first()
        return common_template
        
    
    def transaction_template(self):
        """
        Return default transaction template of tenant if present or else returns 
        transaction template under the tenant(non-default) and if its not 
        present it will return common transaction template else return None
        """
        
        default_template = bulk_models.Template.objects.filter(
            is_default=True, tenant=self, 
            type=bulk_const.TemplateType.TRANSACTION).first()
        if default_template:
            return default_template
        template = bulk_models.Template.objects.filter(
            tenant=self, type=bulk_const.TemplateType.TRANSACTION).first()
        if template:
            return template
        common_template = bulk_models.Template.objects.filter(
            tenant=None, type=bulk_const.TemplateType.TRANSACTION).first()
        return common_template
    
    def ci_section_data(self):
        """
        Return si sections data under a specific tenant.
        """
        tenant_sections = self.ci_theme_sections.all()
        section_data = []
        for tenant_section in tenant_sections:
            section_data.append(tenant_section.section.get_data())
        return section_data


class TenantAdmin(AbstractBaseModel):
    """
    Admins of tenants are saved here. They are the ones with the previlege to 
    manage tenant settings and activity.

    Attribs:
        tenant(obj)     : admin linked tenant object.
        user(obj)       : Admin user object where the basic user details are 
            stored.
        type(int)       : Type of the tenant admin like superadmin, admin..
        

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, 
        related_name='admins', verbose_name=_('Tenant'))
    user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.CASCADE, 
        related_name='tenant_admin', verbose_name=_('Admin User'))
    type = models.IntegerField(
        default=tenant_consts.TenantAdminType.ADMIN, 
        choices=tenant_consts.TenantAdminType.choices, 
        verbose_name=_('Admin Type'))

    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.user.name} - {self.idencode} - {self.tenant.name}'

    class Meta:
        unique_together = ('tenant', 'user')


class Currency(AbstractBaseModel):
    """
    Currencies used in the system.
    Attribs:
        country(obj)    : currency using country.
        name(char)      : name of currency.
        code(char)      : currency code.
    """

    name = models.CharField(
        max_length=1000, verbose_name=_('Currency Name'))
    code = models.CharField(
        max_length=100, default='', null=True, blank=True,
        verbose_name=_('Currency Code'))

    class Meta:
        """Meta Info."""
        verbose_name_plural = _('Currencies')
        ordering = ['name']

    def __str__(self):
        """
        Object value django admin.
        """
        return f'{self.name} - {self.code} - {self.idencode}'


class Country(AbstractBaseModel):
    """
    Model to save countries.

    Attribs:
        name(char)      : name of the country.
        latitude(char)  : latitude of the country.
        longitude(char) : longitude of the country.
        code(char)      : country code.
        dial_code(char) : country dial code.
    """

    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE,
        related_name='countries', verbose_name=_('Currency'),
        null=True, blank=True)
    name = models.CharField(
        max_length=1000, verbose_name=_('Country Name'))
    latitude = models.CharField(
        max_length=500, default='', null=True, blank=True, 
        verbose_name=_('Latitude'))
    longitude = models.CharField(
        max_length=500, default='', null=True, blank=True, 
        verbose_name=_('Longitude'))
    alpha_2 = models.CharField(
        max_length=10, default='', null=True, blank=True,
        verbose_name=_('Country Code'))
    alpha_3 = models.CharField(
        max_length=10, default='', null=True, blank=True,
        verbose_name=_('CCA3 Country Code'))
    dial_code = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('Dial Code'))
    language = models.CharField(
        max_length=10, verbose_name=_('Selected Language'),
        default=user_consts.Language.ENGLISH,
        choices=user_consts.Language.choices)
    score = models.FloatField(default=0.0)
    
    class Meta:
        verbose_name_plural = _('Countries')
        ordering = ['name']
    
    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.alpha_2} - {self.name}'
    
    @property
    def risk_level(self):
        """
        Return risk level of country based on score.
        """
        return risk_models.RiskScore().compute_risk_level(
            self.score)


class Province(AbstractBaseModel):
    """
    Provinces of each countries are stored here.

    Attribs:
        country(obj)    : country of the province.
        name(char)      : name of the province.
        latitude(char)  : latitude of the province.
        longitude(char) : longitude of the province.
    """
    
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, 
        related_name='provinces', verbose_name=_('Country'))
    name = models.CharField(
        max_length=1000, verbose_name=_('Province Name'))
    latitude = models.CharField(
        max_length=500, default='', null=True, blank=True, 
        verbose_name=_('Latitude'))
    longitude = models.CharField(
        max_length=500, default='', null=True, blank=True, 
        verbose_name=_('Longitude'))

    class Meta:
        """"""
        ordering = ['country__name']
    
    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.country.name} - {self.name}  - {self.latitude} - \
            {self.longitude}'


class Region(AbstractBaseModel):
    """
    Region of each province are stored here.

    Attribs:
        province(obj)    : province of the region.
        name(char)      : name of the region.
    """
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE,
        related_name='regions', verbose_name=_('Province'))
    name = models.CharField(
        max_length=1000, verbose_name=_('Region Name'))

    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.province.country.name} - {self.province.name}  - {self.name}'


class Village(AbstractBaseModel):
    """
    Region of each province are stored here.

    Attribs:
        region(obj)    : region of the village.
        name(char)      : name of the region.
    """
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE,
        related_name='villages', verbose_name=_('Region'))
    name = models.CharField(
        max_length=1000, verbose_name=_('Village Name'))

    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.region.province.country.name} - {self.region.province.name} - \
               {self.name}'


class Category(AbstractBaseModel):
    """
    Model to store categories used by tenants in the system.

    Attribs:
        tenant(obj)     : Tenant related to the category.
        name(char)      : Category name.
        type(int)       : Type of the category(choice).
        is_active(bool) : Is cateogry active or not.
    """

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, 
        related_name='categories', verbose_name=_('Tenant'))
    name = models.CharField(
        max_length=1000, default='', null=True, blank=True, 
        verbose_name=_('Category Name'))
    type = models.IntegerField(
        default=tenant_consts.CategoryType.NODE_DOCUMENT, 
        choices=tenant_consts.CategoryType.choices, 
        verbose_name=_('Category Type'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))

    class Meta:
        """Meta Info."""
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def __str__(self):
        """
        Object value django admin.
        """
        return f'{self.name} - {self.get_type_display()} - {self.idencode}'


class Tag(AbstractBaseModel):
    """
    Model to save tags.

    Atribs:
        tenant(obj)   : Tenant which hold the tag.
        name(str): Tag name
        blocked(bool): Is the tag is blocked.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE,
        related_name='tags', verbose_name=_('Tenant'))
    name = models.CharField(
        max_length=200, default='', verbose_name=_('Tag'))
    is_deleted = models.BooleanField(
        default=False, verbose_name=_('Is Deleted'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.name} - {self.idencode}'

    class Meta:
        unique_together = ('tenant', 'name')
