"""Models commonly used in all apps."""

import copy

from django.db import models
from django.contrib.auth.models import UserManager

from utilities.functions import encode, decode

from base import session


@models.Field.register_lookup
class IdencodeLookup(models.lookups.Exact):
    """
    Custom lookup to query id and relationship objects based on encoded ID
    Example:
        User.objects.filter(id__encoded="73YMK7XZRD")
        User.objects.filter(company__encoded="73YMK7XZRD")
    """
    lookup_name = 'encoded'

    def __init__(self, lhs, rhs):
        try:
            rhs = decode(rhs)
        except ValueError as e:
            rhs = -1
        super(IdencodeLookup, self).__init__(lhs, rhs)

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s = %s' % (lhs, rhs), params


models.IntegerField.register_lookup(IdencodeLookup)
models.ForeignKey.register_lookup(IdencodeLookup)
models.ManyToManyField.register_lookup(IdencodeLookup)


class CustomManager(models.Manager):
    """
    Custom manager with added query options
    """

    def get_by_encoded_id(self, encoded_id):
        """
        To get an object using and encoded ID
        """
        return self.get(id__encoded=encoded_id)


class CustomUserManager(UserManager):
    """
    Custom user manager with added query options
    """

    def get_by_encoded_id(self, encoded_id):
        """
        To get an object using and encoded ID
        """
        return self.get(id__encoded=encoded_id)


class AbstractBaseModel(models.Model):
    """
    Abstract base model for tracking.

    Atribs:
        creator(obj): Creator of the object
        updater(obj): Updater of the object
        created_on(datetime): Added date of the object
        updated_on(datetime): Last updated date of the object
    """
    creator = models.ForeignKey(
        "accounts.CustomUser", default=None, null=True,
        blank=True, related_name="creator_%(class)s_objects",
        on_delete=models.SET_NULL)
    updater = models.ForeignKey(
        "accounts.CustomUser", default=None, null=True,
        blank=True, related_name="updater_%(class)s_objects",
        on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    objects = CustomManager()

    class Meta:
        """Meta class for the above model."""

        abstract = True
        ordering = ('-created_on',)
    
    def save(self, *args, **kwargs):
        current_user = session.get_current_user()
        if current_user:
            if not self.id:
                self.creator = current_user
            self.updater = current_user
        super(AbstractBaseModel, self).save(*args, **kwargs)

    @property
    def idencode(self):
        """To return encoded id."""
        return encode(self.id)

    @classmethod
    def field_names(cls) -> list:
        return [field.name for field in cls._meta.get_fields()]

    @classmethod
    def clean_dict(cls, data: dict, extra_keys: set = None) -> dict:
        # Patch for multipart request with file
        # 1. AttributeError: 'NoneType' object has no attribute 'seek'
        #    Occurs on deepcopy
        # 2. Reinserting image to validated_data

        image = data.pop('image', None)
        extra_keys = extra_keys or set()
        n_data = copy.deepcopy(data)
        keys_needed = set(cls.field_names()) | extra_keys
        keys_to_remove = list(keys_needed ^ {*n_data})
        [n_data.pop(key, None) for key in keys_to_remove]
        if image:
            data['image'] = image
            if 'image' in keys_needed:
                n_data['image'] = image
        return n_data

    @classmethod
    def get_by_encoded_id(cls, encoded_id: str):
        return cls.objects.get(id=decode(encoded_id))


class Address(models.Model):
    """
    Abstract model to group fields related to address
    """
    house_name = models.CharField(
        max_length=100, default='', null=True, blank=True)
    street = models.CharField(
        max_length=500, default='', null=True, blank=True)
    city = models.CharField(
        max_length=500, default='', null=True, blank=True)
    sub_province = models.CharField(
        max_length=500, default='', null=True, blank=True)
    province = models.CharField(
        max_length=500, default='', null=True, blank=True)
    country = models.CharField(
        max_length=500, default='', null=True, blank=True)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    zipcode = models.CharField(
        max_length=50, default='', null=True, blank=True)

    class Meta:
        """
        Meta class defines class level configurations
        """
        abstract = True


class NumberedModel(models.Model):
    """
    Abstract base class to use to automatically add a number field
    to track a number tracked that can be shown in the frontend.
    """
    number = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(NumberedModel, self).save(*args, **kwargs)
        if not self.number:
            self.number = self.id + 1000
            self.save()


class GraphModel(models.Model):
    """
    Abstract model for creating Directed Acyclic Graph.
    Useful for creating transaction graph

    """

    class Meta:
        ordering = ('-id',)
        abstract = True

    def __unicode__(self):
        return u"%s" % self.pk

    def add_parent(self, ancestor):
        """ Function to add a parent """
        self.circular_checker(ancestor, self)
        self.parents.add(ancestor)
        self.save()

    def add_child(self, child):
        """ Function to add a child """
        child.add_parent(self)

    def remove_parent(self, ancestor):
        """ Function to remove a parent """
        self.parents.remove(ancestor)
        self.save()

    def remove_child(self, child):
        """ Function to remove a child """
        child.remove_parent(self)

    def get_descendants(self, include_self=False):
        """ Gets all children and their children recursively"""
        descendants_set = self.children.all().order_by('-id').distinct('id')
        for child in self.children.all():
            grand_children = child.get_descendants()
            descendants_set |= grand_children
        if include_self:
            descendants_set |= self.__class__.objects.filter(id=self.id).order_by('-id').distinct('id')
        return descendants_set

    def get_ancestors(self, include_self=False):
        """ Gets all parents and their parents recursively"""
        ancestors_set = self.parents.all().order_by('-id').distinct('id')
        for parent in self.parents.all():
            grand_parent = parent.get_ancestors()
            ancestors_set |= grand_parent
        if include_self:
            ancestors_set |= self.__class__.objects.filter(id=self.id).order_by('-id').distinct('id')
        return ancestors_set

    def get_leaf_nodes(self):
        """ Gets the ending nodes """
        leaf_nodes = self.__class__.objects.none()
        children = self.children.all().order_by('-id').distinct('id')
        if not children:
            return self.__class__.objects.filter(id=self.id).order_by('-id').distinct('id')
        for child in children:
            leaf_nodes |= child.get_leaf_nodes()
        return leaf_nodes

    def get_root_nodes(self):
        """ Gets the starting nodes """
        root_nodes = self.__class__.objects.none()
        parents = self.parents.all().order_by('-id').distinct('id')
        if not parents:
            return self.__class__.objects.filter(id=self.id).order_by('-id').distinct('id')
        for parent in parents:
            root_nodes |= parent.get_root_nodes()
        return root_nodes

    def is_island(self):
        """ Check if node is separated from the rest of the graph"""
        return not bool(self.parents.all() or self.children.all())

    @staticmethod
    def circular_checker(parent, child):
        """
        Checks that the object is not an ancestor, avoid self links
        """
        if parent == child:
            raise ValueError('Self links are not allowed.')
        if child in parent.get_ancestors():
            raise ValueError('The object is an ancestor.')
