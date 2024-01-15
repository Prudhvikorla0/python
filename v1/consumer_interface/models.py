"""Models of the app Consumer Interface."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation

from common.library import _get_file_path

from base.models import AbstractBaseModel

from v1.consumer_interface import constants as ci_consts


class BasicSection(AbstractBaseModel):
    """
    Basic Abstract model for themes like consumer interfce.
    """
    
    name = models.CharField(
        max_length=500, default="", null=True, blank=True, 
        verbose_name="Section Name")
    key = models.CharField(
        max_length=50, default="", null=True, blank=True, 
        verbose_name="Section Key")
    position = models.PositiveIntegerField(
        default=1, verbose_name="Section Position")
    is_default = models.BooleanField(
        default=False, verbose_name='Is Default Section')
    sections = GenericRelation(
        'SectionTenantRegister', related_query_name='ci_sections',
        object_id_field='section_object_id',content_type_field='section_type')
    
    def __str__(self) -> str:
        """
        Return custom object name.
        """
        return f'{self.name} : {self.idencode}({self.id})'
    
    def save(self, *args, **kwargs):
        """
        Sets name and key during the object creation.
        """
        if not self.id:
            self.name = self.__class__.__name__
            self.key = self.__class__.__name__.lower()
        return super().save(*args, **kwargs)
    
    def removable_fields(self):
        """
        Return list of not neccessary fields in response.
        """
        fields = [
            'creator', 'updater','created_on','is_default',
            'updated_on','id','sections',
            ]
        return fields
    
    def get_data(self):
        """
        Method returns object data.
        """
        data_dict = {}
        for field in self.__class__._meta.get_fields():
            if field.name in self.removable_fields():
                continue
            field_name = field.name
            field_value = getattr(self, field_name,None)
            if not field_value:
                field_value = None
            if (type(field) == models.FileField) and field_value:
                field_value = field_value.url
            if type(field) == models.ManyToManyField and field_value:
                list_data = []
                for field in field_value.all().order_by('position'):
                    list_data.append(field.get_data())
                field_value = list_data
            data_dict[field_name] = field_value
        return data_dict
    
    class Meta:
        """
        Meta overrided to make the class abstract.
        """
        abstract = True


class CICard(AbstractBaseModel):
    """
    Model to save cards used in the ci theme.
    """
    image = models.FileField(
        upload_to=_get_file_path, blank=True, null=True, 
        verbose_name=_('Card Image'))
    title = models.CharField(
        max_length=2000, default="", null=True, blank=True, 
        verbose_name="Card Title")
    file = models.FileField(
        upload_to=_get_file_path, blank=True, null=True, 
        verbose_name=_('Card File'))
    position = models.PositiveIntegerField(
        default=1, verbose_name="Card Position")
    
    def __str__(self) -> str:
        return f'{self.title} : {self.idencode}'
    
    def removable_fields(self):
        """
        Return list of not neccessary fields in response.
        """
        fields = [
            'creator', 'updater','created_on',
            'updated_on','id',
            ]
        return fields
    
    def get_data(self):
        """
        Method returns object data.
        """
        data_dict = {}
        for field in self.__class__._meta.fields:
            if field.name in self.removable_fields():
                continue
            field_name = field.name
            field_value = getattr(self, field_name,None)
            if not field_value:
                field_value = None
            if (type(field) == models.FileField) and field_value:
                field_value = field_value.url
            data_dict[field_name] = field_value
        return data_dict


class Header(BasicSection):
    """
    Model to save Header section static data of consumer interface.
    """
    logo = models.FileField(
        upload_to=_get_file_path, blank=True, null=True, 
        verbose_name=_('CI Logo'))


class OverViewSection(BasicSection):
    """
    Model to save OverView section static data of consumer interface.
    """
    image = models.FileField(
        upload_to=_get_file_path, blank=True, null=True, 
        verbose_name=_('Overview Image'))
    title = models.CharField(
        max_length=2000, default="", null=True, blank=True, 
        verbose_name="Overview Title")
    link = models.URLField(
        default=None, null=True, blank=True, verbose_name="Site Link")


class InfoSection(BasicSection):
    """
    Model to save Info section static data of consumer interface.
    """
    image = models.FileField(
        upload_to=_get_file_path, blank=True, null=True, 
        verbose_name=_('InfoView Image'))
    subtitle = models.CharField(
        max_length=2000, default="", null=True, blank=True, 
        verbose_name="InfoView SubTitle")
    title = models.CharField(
        max_length=2000, default="", null=True, blank=True, 
        verbose_name="InfoView Title")
    subheading = models.CharField(
        max_length=2000, default="", null=True, blank=True, 
        verbose_name="InfoView SubHeading")


class MapSection(BasicSection):
    """
    Model to save Map section static data of consumer interface.
    """
    pass


class SupplyChainSection(BasicSection):
    """
    Model to save SupplyChain section static data of consumer interface.
    """
    title = models.CharField(
        max_length=2000, default="", null=True, blank=True, 
        verbose_name="SupplyChain Info Title")
    

class AboutSection(BasicSection):
    """
    Model to save Info section static data of consumer interface.
    """
    image = models.FileField(
        upload_to=_get_file_path, blank=True, null=True, 
        verbose_name=_('About Image'))
    title = models.CharField(
        max_length=2000, default="", null=True, blank=True, 
        verbose_name="About Title")
    description = models.TextField(
        default="", null=True, blank=True, 
        verbose_name="About Description")
    website_link = models.URLField(
        default=None, null=True, blank=True, 
        verbose_name="About Wbesite")
    website_link_text = models.CharField(
        max_length=5000,default=None, null=True, blank=True, 
        verbose_name="About Wbesite Button Text")
    

class MoreInfoSection(BasicSection):
    """
    Model to save MoreInfo section static data of consumer interface.
    """
    image = models.FileField(
        upload_to=_get_file_path, blank=True, null=True, 
        verbose_name=_('MoreInfo Image'))
    subtitle = models.CharField(
        max_length=2000, default="", null=True, blank=True, 
        verbose_name="Moreinfo SubTitle")
    title = models.CharField(
        max_length=2000, default="", null=True, blank=True, 
        verbose_name="Moreinfo Title")
    description = models.TextField(
        default="", null=True, blank=True, 
        verbose_name="Moreinfo Description")
    cards = models.ManyToManyField(
        CICard,default=None,blank=True, related_name='more_infos')
 

class Footer(BasicSection):
    """
    Model to save Footer section static data of consumer interface.
    """
    logo = models.FileField(
        upload_to=_get_file_path, blank=True, null=True, 
        verbose_name=_('CI Logo'))


class SectionTenantRegister(AbstractBaseModel):
    """
    Model to save ci sections under a tenant.
    """

    tenant = models.ForeignKey(
        'tenants.Tenant', null=True, default=None,
        on_delete=models.CASCADE, related_name='ci_theme_sections', 
        verbose_name=_('Tenant'),blank=True)
    section_type = models.ForeignKey(
        ContentType, related_name="section_types", 
        on_delete=models.SET_NULL, null=True,
        limit_choices_to={
        'model__in': ci_consts.TENANT_SECTION_GENERIC_MODELS})
    section_object_id = models.PositiveIntegerField(null=True, blank=True)
    section = GenericForeignKey('section_type', 'section_object_id')
    is_removed = models.BooleanField(default=False)

    @property
    def tenant_name(self):
        """
        Return tenant name.
        """
        try:
            return self.tenant.name
        except:
            return ""

    def __str__(self) -> str:
        """
        Return custom object name.
        """
        return f'{self.tenant_name} : {self.idencode}({self.section.name})'


class CITheme(AbstractBaseModel):
    """
    ci theme related data stored here.

    Attribs:
        tenant(obj)         : tenant who holds the theme.
        supply_chains(objs) : supply chains of the tenant which holds the 
            tracker theme
        default(bool)       : Is the theme is the default theme.
    """
    name = models.CharField(
        max_length=500, default="", null=True, blank=True, 
        verbose_name="Theme Name")
    tenant = models.ForeignKey(
        'tenants.Tenant', null=True, default=None,
        on_delete=models.CASCADE, related_name='ci_themes', 
        verbose_name=_('Tenant'))
    is_default = models.BooleanField(
        default=False, verbose_name=_('Is Default Theme'))
    is_current = models.BooleanField(
        default=False, verbose_name=_('Is Current Theme'))

    primary_colour = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Primary Colour'))
    secondary_colour = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Secondary Colour'))

    background_colour_alpha = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Background Colour Alpha'))
    background_colour_beta = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Background Colour Beta'))
    
    text_colour_primary = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Text Colour Primary'))
    text_colour_secondary = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Text Colour Secondary'))
    text_colour_alpha = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Text Colour Alpha'))
    text_colour_beta = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Text Colour Beta'))
    
    def __str__(self) -> str:
        return f'{self.tenant.name} : {self.idencode}'
