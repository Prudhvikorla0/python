"""Models of the app Dashboard."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.constraints import UniqueConstraint

from common.library import _get_file_path

from base.models import AbstractBaseModel


class DashboardTheme(AbstractBaseModel):
    """
    Dashboard theme related data are stored here.

    Attribs:
        tenant(obj)    : tenant who holds the theme.
        default(bool)  : Is the theme is the default theme.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    tenant = models.ForeignKey(
        'tenants.Tenant', null=True, default=None,
        on_delete=models.CASCADE, related_name='dashboard_theme', 
        verbose_name=_('Tenant'))
    is_default = models.BooleanField(
        default=False, verbose_name=_('Is Default Theme'))

    image = models.FileField(upload_to=_get_file_path, blank=True, null=True)

    colour_primary_alpha = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Primary Colour Aplpha'))
    colour_primary_beta = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Primary Colour Beta'))
    colour_primary_gamma = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Primary Colour Gamma'))
    colour_primary_delta = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Primary Colour Delta'))

    colour_secondary = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Secondary Colour'))

    colour_font_alpha = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Font Colour Aplpha'))
    colour_font_beta = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Font Colour Beta'))
    colour_font_negative = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Font Colour Negative'))

    colour_border_alpha = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Boarder Colour Aplpha'))
    colour_border_beta = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Boarder Colour Beta'))

    colour_background_alpha = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Background Colour Alpha'))
    colour_background_beta = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Background Colour Beta'))
    
    colour_sidebar = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Sidebar Colour'))

    danger_color = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Danger Colour'))
    success_color = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Success Colour'))
    warning_color = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Warning Colour'))
    error_text_color = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Error Text Colour'))
    pending_color = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Pending Colour'))
    approved_color = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Approved Colour'))
    rejected_color = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Rejected Colour'))
    placeholder_color = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Placeholder Colour'))
    

    def __str__(self):
        """Object name in django admin."""
        return f'{self.tenant.name} - {self.idencode}'

    def save(self, *args, **kwargs):
        """Save overrided to add only single default theme."""
        if self.is_default:
            try:
                DashboardTheme.objects.exclude(id=self.id).update(
                    is_default=False)
            except:
                pass
        return super().save(*args, **kwargs)


class TrackerTheme(AbstractBaseModel):
    """
    Tracker theme related data stored here.

    Attribs:
        tenant(obj)         : tenant who holds the theme.
        supply_chains(objs) : supply chains of the tenant which holds the 
            tracker theme
        default(bool)       : Is the theme is the default theme.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """
    name = models.CharField(
        max_length=500, default="", null=True, blank=True, 
        verbose_name="Theme Name")
    tenant = models.ForeignKey(
        'tenants.Tenant', null=True, default=None,
        on_delete=models.CASCADE, related_name='tracker_themes', 
        verbose_name=_('Tenant'))
    supply_chains = models.ManyToManyField(
        'supply_chains.SupplyChain', blank=True, related_name='tracker_themes',
        verbose_name=_('Supplychains'))
    node = models.ForeignKey(
        'nodes.Node', null=True, default=None,
        on_delete=models.SET_NULL, related_name='tracker_theme', 
        verbose_name=_('Node'))
    batch = models.ForeignKey(
        'products.Batch', null=True, default=None,
        on_delete=models.SET_NULL, related_name='tracker_theme', 
        verbose_name=_('Default Batch'))
    is_default = models.BooleanField(
        default=False, verbose_name=_('Is Default Theme'))
    logo = models.FileField(
        upload_to=_get_file_path, blank=True, null=True, 
        verbose_name=_('Tracker Logo'))

    primary_colour = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Primary Colour'))
    secondary_colour = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Secondary Colour'))
    colour_background_alpha = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Background Colour Alpha'))
    primary_white = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Primary White'))
    
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
    text_colour_gamma = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Text Colour Gamma'))
    text_colour_delta = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Text Colour Delta'))
    map_text_colour = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Text Colour In Map'))

    shade_colour_alpha = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Shade Colour Alpha'))
    shade_colour_beta = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Shade Colour Beta'))
    shade_colour_gamma = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Shade Colour Gamma'))

    header_boarder_colour = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Border Colour Of Header'))
    
    txn_type_colour_alpha = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Transaction Type Colour Alpha'))
    txn_type_colour_beta = models.CharField(
        default="", null=True, blank=True, max_length=20, 
        verbose_name=_('Transaction Type Colour Beta'))

    class Meta:
        """Meta setup"""
        unique_together = ('tenant', 'name',)

    def __str__(self):
        """Object name in django admin."""
        return f'{self.tenant.name} - {self.idencode}'

    def save(self, *args, **kwargs):
        """Save overrided to add only single default theme."""
        if self.is_default:
            try:
                DashboardTheme.objects.exclude(id=self.id).update(
                    is_default=False)
            except:
                pass
        return super().save(*args, **kwargs)
