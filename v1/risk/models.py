# Risk Analysis Models

import copy

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import AbstractBaseModel
from base import session
from base import exceptions
from common.library import string_date_to_date

from v1.risk.integrations.roai import apis as roai_apis

from . import constants


class RiskScore(AbstractBaseModel):
    """
    Model to store the risk score of a Node
    """
    node = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE,
        related_name='risk_scores', verbose_name=_('Node'))
    year = models.IntegerField(default=1970)

    environment = models.FloatField(default=0.0)
    social = models.FloatField(default=0.0)
    governance = models.FloatField(default=0.0)
    overall = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('node', 'year')

    def __str__(self):
        return f"{self.node.name} - {self.year}"

    @staticmethod
    def compute_risk_level(score):
        if score <= 43:
            return constants.Severity.HIGH
        if score <= 60:
            return constants.Severity.MEDIUM
        return constants.Severity.LOW

    @property
    def environment_risk_level(self):
        return self.compute_risk_level(self.environment)

    @property
    def social_risk_level(self):
        return self.compute_risk_level(self.social)

    @property
    def governance_risk_level(self):
        return self.compute_risk_level(self.governance)

    @property
    def overall_risk_level(self):
        return self.compute_risk_level(self.overall)

    @property
    def high_severity_comments(self):
        return self.comments.filter(severity=constants.Severity.HIGH)

    @property
    def medium_severity_comments(self):
        return self.comments.filter(severity=constants.Severity.MEDIUM)

    def update_category_rl_scores(self, cat_type: int, risk_level: int, category_scores: dict):
        category, _ = CategoryScore.objects.get_or_create(
            score=self, category=cat_type, risk_level=risk_level)
        score = category_scores.get('score', 0)
        category.total = category_scores.get('total', score)
        category.average = category_scores.get('avg', score)
        category.applicable_indicators = category_scores['applicable_indicators']
        return True

    def update_risk_level_scores(self, risk_level: int, scores: dict):
        scores = copy.deepcopy(scores)
        environment = scores.pop('environment')
        social = scores.pop('social')
        governance = scores.pop('governance')
        overall = scores
        self.update_category_rl_scores(
            constants.Category.ENVIRONMENT, risk_level, environment)
        self.update_category_rl_scores(
            constants.Category.SOCIAL, risk_level, social)
        self.update_category_rl_scores(
            constants.Category.GOVERNANCE, risk_level, governance)
        self.update_category_rl_scores(
            constants.Category.OVERALL, risk_level, overall)

        return True

    def update_all_score(self, score_data: dict):
        # risky_scores = score_data['risk'] # TODO: Risky and Safe are commented keys are missing.
        # safe_scores = score_data['safe']
        all_scores = score_data['overall']
        # self.update_risk_level_scores(constants.RiskLevel.RISKY, risky_scores)
        # self.update_risk_level_scores(constants.RiskLevel.SAFE, safe_scores)
        self.update_risk_level_scores(constants.RiskLevel.ALL, all_scores)
        self.environment = all_scores['environment']['score']
        self.social = all_scores['social']['score']
        self.governance = all_scores['governance']['score']
        self.overall = all_scores['score']
        self.save()

        self.comments.all().delete()

        severity_map = {
            'low': constants.Severity.LOW,
            'medium': constants.Severity.MEDIUM,
            'high': constants.Severity.HIGH,
        }
        for comment in score_data['specs']:
            RiskComment.objects.create(
                score=self, comment=comment['description'],
                severity=severity_map[comment['severity']]
            )
        return True

    @classmethod
    def update_node_score(cls, node):
        """
        Function to find the score of the node and update it
        """
        cls.update_node(node)
        score_data = cls.get_score(node)
        cls.update_node_certifications(node, score_data['certifications'])
        score, _ = cls.objects.get_or_create(
            node=node, year=score_data['year'])
        score.update_all_score(score_data)
        return True

    @classmethod
    def update_node(cls, node):
        from v1.nodes.serializers.node import NodeSerializer
        node_data = dict(NodeSerializer(node).data)

        addl_prof_data = node.submission_form.export_as_dict() if node.submission_form else {}
        invite_questionnaire = node.inviter_questionnaire.export_as_dict(
        ) if node.inviter_questionnaire else {}
        signup_questionnaire = node.signup_questionnaire.export_as_dict(
        ) if node.inviter_questionnaire else {}

        node_data = {
            'reference': node.idencode,
            'is_test': settings.DEBUG,
            **node_data,
            **addl_prof_data,
            **invite_questionnaire,
            **signup_questionnaire,
            'address': {
                "street_1": node.street or "",
                "street_2": node.street or "",
                "city": node.city or "",
                "state": node.province.name if node.province else "",
                "postal_code": node.zipcode or "",
                "country_code": node.country.alpha_3.lower(),
            }, 
            "phone": node.phone # TODO: got error related to phone number structure
        }
        for k, v in node_data.items():
            if v is None:
                node_data[k] = ""

        resp = roai_apis.NodeAPI(
            node_data=node_data, ro_number=node.ro_number).call()
        node.ro_number = resp['id']
        node.save()
        return True
    
    @classmethod
    def update_node_certifications(cls, node, certifications):
        """
        Update node certifications from ro-ai to ro.
        """
        from v1.claims.models import NodeClaim, Claim
        from v1.claims import utilities as claim_utils
        from v1.claims import constants as claim_consts

        for certification in certifications:
            standard_id = certification['standard']['id']
            if not node.node_claims.filter(
                claim__standard_id=standard_id).exists():
                try:
                    claims = Claim.objects.filter(standard_id=standard_id)
                    if not claims:
                        claim_utils.sync_standard_from_roai(node.tenant, True)
                        claims = Claim.objects.filter(standard_id=standard_id)
                    claim = claims.first()
                except:
                    continue
                data = {
                    'node': node, 
                    'claim': claim, 
                    'attached_to': claim_consts.ClaimAttachedTo.NODE, 
                    'attached_by': node, 
                    'attached_via': claim_consts.ClaimAttachedVia.SYNC, 
                    'certification_number': certification['certificate_no'], 
                    'certification_date': certification['start_date'], 
                    'expiry_date': string_date_to_date(
                        certification['anniversary_date'])
                }
                NodeClaim.objects.create(**data)
        return True

    @classmethod
    def get_score(cls, node):
        if not node.ro_number:
            cls.update_node(node)
        return roai_apis.GetScore(node.ro_number).call()


class CategoryScore(AbstractBaseModel):
    """
    Model to store scored for each categories.
    """
    score = models.ForeignKey(
        RiskScore, on_delete=models.CASCADE,
        related_name="categories", verbose_name=_('Category Score'))
    total = models.FloatField(default=0.0)
    average = models.FloatField(default=0.0)
    applicable_indicators = models.IntegerField(default=0)

    risk_level = models.IntegerField(
        choices=constants.RiskLevel.choices, default=constants.RiskLevel.RISKY)
    category = models.IntegerField(
        choices=constants.Category.choices, default=constants.Category.ENVIRONMENT)

    class Meta:
        unique_together = ('score', 'risk_level', 'category')

    def __str__(self):
        return f"{self.score} - {self.category} - {self.risk_level}"


class RiskComment(AbstractBaseModel):
    """
    Model to store comments about Risk Analysis
    """
    score = models.ForeignKey(
        RiskScore, on_delete=models.CASCADE,
        related_name="comments", verbose_name=_('Risk Comments'))
    comment = models.CharField(max_length=2000)
    severity = models.IntegerField(
        choices=constants.Severity.choices, default=constants.Severity.HIGH)

    def __str__(self):
        return f"{self.score} - {self.severity} - {self.comment[:10]}"
