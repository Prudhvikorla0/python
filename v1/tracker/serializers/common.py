

from rest_framework import serializers

from common.drf_custom import fields as custom_fields

from v1.products import models as prod_models

from v1.claims import models as claim_models

from v1.supply_chains import models as sc_models

from v1.nodes import models as node_models

from v1.tenants import constants as tenant_consts


class ProductBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for products..
    """
    
    name = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = prod_models.Product
        fields = ('name', 'image',)
        ref_name='TrackerProductSerializer'


class AttachedClaimBaseSerialier(serializers.ModelSerializer):
    """
    Base serializer for claims.
    """
    name = serializers.CharField(read_only=True,source='claim.name')

    class Meta:
        """
        Meta Info.
        """
        model = claim_models.AttachedClaim
        fields = ('name',)


class OperationBaseSerializer(serializers.ModelSerializer):
    """
    Serializer for operations(actors types)
    """
    id = custom_fields.IdencodeField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = serializers.FileField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = sc_models.Operation
        fields = ('id', 'name', 'image',)


class NodeSerializer(serializers.ModelSerializer):
    """
    """
    id = custom_fields.IdencodeField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True)
    operation = serializers.CharField(read_only=True, source='operation.name')
    country = custom_fields.CharListField(
        read_only=True, source='country.name')
    province = custom_fields.CharListField(
        read_only=True, source='province.name')
    latitude = serializers.FloatField(
        read_only=True,source='province.latitude')
    longitude = serializers.FloatField(
        read_only=True,source='province.longitude')

    class Meta:
        """
        """
        model = node_models.Node
        fields = (
            'id','name', 'image', 'operation', 'country', 'province', 
            'latitude', 'longitude',
            )
        ref_name='TrackerNodeSerializer'

    def to_representation(self, instance):
        """
        Overrided to set values on the basis of node data tranparency.
        """
        data = super().to_representation(instance)
        tenant = instance.tenant
        node_transparency = \
            tenant_consts.NodeDataTransparency.PARTIALY_TRANSPARENT
        if (tenant.node_data_transparency == node_transparency):
            update_dict = {
                "name": "●●●●●●",
                "image": None,
            }
            data.update(update_dict)
        return data
