"""Serializers related to country related apis."""

from rest_framework import serializers

from common.drf_custom import fields as custom_fields

from v1.tenants import models as tenant_models
from v1.tenants.serializers.currency import CurrencySerializer


class VillageSerializer(serializers.ModelSerializer):
    """
    Serializer for Region data.
    """
    id = custom_fields.IdencodeField(read_only=True)
    region = custom_fields.IdencodeField(
        write_only=True, related_model=tenant_models.Region)

    class Meta:
        """
        Meta Info.
        """
        model = tenant_models.Village
        exclude = ('creator', 'updater', 'created_on', 'updated_on', )


class RegionSerializer(serializers.ModelSerializer):
    """
    Serializer for Region data.
    """
    id = custom_fields.IdencodeField(read_only=True)
    villages = custom_fields.ManyToManyIdencodeField(
        serializer=VillageSerializer, read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = tenant_models.Region
        exclude = ('creator', 'updater', 'created_on', 'updated_on', 'province')


class ProvinceSerializer(serializers.ModelSerializer):
    """
    Serializer for country data.
    """

    id = custom_fields.IdencodeField(read_only=True)
    regions = custom_fields.ManyToManyIdencodeField(
        serializer=RegionSerializer, read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = tenant_models.Province
        exclude = ('creator', 'updater', 'created_on', 'updated_on', 'country')


class CountrySerializer(serializers.ModelSerializer):
    """
    Serializer for province data.
    """

    id = custom_fields.IdencodeField(read_only=True)
    provinces = custom_fields.ManyToManyIdencodeField(
        serializer=ProvinceSerializer, read_only=True)
    currency = custom_fields.IdencodeField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = tenant_models.Country
        exclude = ('creator', 'updater', 'created_on', 'updated_on')


class BaseCountrySerializer(serializers.ModelSerializer):
    """
    Serializer for province data.
    """

    id = custom_fields.IdencodeField(read_only=True)
    name = serializers.CharField(read_only=True)
    class Meta:
        """
        Meta Info.
        """
        model = tenant_models.Country
        fields = ('id', 'name',)


class BaseRegionSerializer(serializers.ModelSerializer):
    """
    Serializer for Region data.
    """
    id = custom_fields.IdencodeField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = tenant_models.Region
        fields = ('id', 'name')


class BaseProvinceSerializer(serializers.ModelSerializer):
    """
    Serializer for country data.
    """

    id = custom_fields.IdencodeField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = tenant_models.Province
        fields = ('id', 'name')
