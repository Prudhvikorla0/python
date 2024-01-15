from rest_framework import serializers
from v1.risk import models as risk_models

from common.drf_custom import fields as custom_fields


class RiskCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for RiskComment
    """
    id = custom_fields.IdencodeField(read_only=True)
    score = custom_fields.IdencodeField(read_only=True)

    class Meta:
        model = risk_models.RiskComment
        exclude = (
            'updater', 'creator', 'updated_on', 'created_on',
            )


class RiskScoreSerializer(serializers.ModelSerializer):
    """
    Serializer for RiskScore
    """

    id = custom_fields.IdencodeField(read_only=True)
    node = custom_fields.IdencodeField(read_only=True)
    high_severity_comments = custom_fields.ManyToManyIdencodeField(
        serializer=RiskCommentSerializer)
    medium_severity_comments = custom_fields.ManyToManyIdencodeField(
        serializer=RiskCommentSerializer)
    environment = custom_fields.RoundingDecimalField(max_digits=5, decimal_places=2)
    social = custom_fields.RoundingDecimalField(max_digits=5, decimal_places=2)
    governance = custom_fields.RoundingDecimalField(max_digits=5, decimal_places=2)
    overall = custom_fields.RoundingDecimalField(max_digits=5, decimal_places=2)

    environment_risk_level = serializers.IntegerField(read_only=True)
    social_risk_level = serializers.IntegerField(read_only=True)
    governance_risk_level = serializers.IntegerField(read_only=True)
    overall_risk_level = serializers.IntegerField(read_only=True)

    class Meta:
        model = risk_models.RiskScore
        exclude = (
            'updater', 'creator', 'updated_on', 'created_on',
            )

