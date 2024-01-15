from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from common.drf_custom import fields
from base import session
from base import exceptions
from common.library import _pop_out_from_dictionary

from v1.questionnaire import models as question_models
from v1.questionnaire import constants as question_consts

from v1.supply_chains import models as sc_models
from v1.supply_chains.serializers import supply_chain as sc_serializers

from v1.nodes.serializers import node as node_serializers
from v1.nodes import models as node_models

from v1.bulk_templates import models as bulk_models

from v1.tenants.serializers import tenant as tenant_serializer
from v1.tenants import models as tenant_models


class QuestionnaireSerializer(serializers.ModelSerializer):
    """
    Serializer for questionnaire model.
    """
    id = fields.IdencodeField(read_only=True)
    tags = fields.ManyToManyIdencodeField(
        serializer=tenant_serializer.TagSerializer, 
        related_model=tenant_models.Tag, 
        required=False)
    status = serializers.IntegerField(required=False)
    submitted_date = serializers.DateField(
        required=False, input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    bulk_upload = fields.IdencodeField(
        write_only=True,required=False,related_model=bulk_models.BulkUpload)

    class Meta:
        """
        """
        model = question_models.Questionnaire
        fields = (
            'id','name','submitter','submitted_date',
            'status','tags','total_questions','bulk_upload',)
        
    def create(self, validated_data):
        """
        Create Overrided to update questionnaire owner.
        """
        validated_data.pop('status',None)
        bulk_upload =  validated_data.pop('bulk_upload',None)
        validated_data['owner'] = session.get_current_node()
        questionnaire = super().create(validated_data)
        if bulk_upload:
            bulk_extra_data = {
                "questionnaire": questionnaire.idencode
            }
            try:
                bulk_upload.start_upload(bulk_extra_data)
            except:
                raise exceptions.BadRequest(_("Bulk Upload already exists"))
        return questionnaire

    def update(self, instance, validated_data):
        """
        Update overrided to update only specified fields.
        """
        pop_fields = ['status',]
        validated_data = _pop_out_from_dictionary(
            validated_data,pop_fields)
        return super().update(instance, validated_data)
    

class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for answers.
    """
    id = fields.IdencodeField(read_only=True)
    question = fields.IdencodeField(
        related_model=question_models.Question,write_only=True)
    files = fields.ManyToManyIdencodeField(
        serializer=node_serializers.BasicNodeDocumentSerializer,
        related_model=node_models.NodeDocument,required=False)
    type = serializers.IntegerField(read_only=True)
    questionnaire_status = serializers.IntegerField(
        source='question.questionnaire.status',read_only=True)
    
    class Meta:
        """
        Meta Info.
        """
        model = question_models.Answer
        fields = ('id','answer','question','files','type',
                  'questionnaire_status')

    def create(self, validated_data):
        """
        Create overrided to update type of answer.
        """
        validated_data['type'] = question_consts.AnswerType.MANUAL
        answer = super().create(validated_data)
        questionnaire = validated_data['question'].questionnaire
        if questionnaire.all_questions_answered():
            questionnaire.answer_generation_complete()
        return answer
    
    def update(self, instance, validated_data):
        """
        Update overrided to change the answer type.
        """
        if instance.type == question_consts.AnswerType.AUTOMATIC:
            validated_data['type'] = question_consts.AnswerType.BOTH
        return super().update(instance, validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for questions.
    """
    id = fields.IdencodeField(read_only=True)
    questionnaire = fields.IdencodeField(
        write_only=True,related_model=question_models.Questionnaire)
    answer = AnswerSerializer(read_only=True)
    questionnaire_status = serializers.IntegerField(
        source='questionnaire.status',read_only=True)
    
    def validate(self, attrs):
        """
        Validate question already exists or not.
        """
        questionnaire = attrs.get(
            'questionnaire',None)
        if not questionnaire:
            questionnaire = self.instance.questionnaire
        if questionnaire.status == question_consts.QuestionnaireStatus.APPROVED:
            raise exceptions.BadRequest(_("Questionnaire is already approved"))
        old_questions = question_models.Question.objects.filter(
            question__iexact=attrs['question'], questionnaire=questionnaire,
            is_deleted=False)
        if old_questions.exists():
            raise exceptions.BadRequest(_("Question already exists"))
        return super().validate(attrs)

    class Meta:
        """
        Meta info.
        """
        model = question_models.Question
        fields = (
            'id','questionnaire','question','answer',
            'is_answered','answer_generating','questionnaire_status',)
        
    def create(self, validated_data):
        """
        Method overrided to change the status of a deleted question.
        """
        questionnaire = validated_data['questionnaire']
        old_questions = question_models.Question.objects.filter(
            question__iexact=validated_data['question'], 
            questionnaire=validated_data['questionnaire'])
        if questionnaire.status != question_consts.QuestionnaireStatus.GENERATING_ANSWER:
            questionnaire.status = question_consts.QuestionnaireStatus.GENERATING_ANSWER
            questionnaire.save()
        if old_questions.exists():
            question = old_questions.first()
            question.is_deleted = False
            question.save()
            return question
        return super().create(validated_data)


class PublicQuestionnaireSerializer(serializers.ModelSerializer):
    """
    Serializer for public data to be shown related to questionnaire.
    """
    name = serializers.CharField(read_only=True)
    submitter = serializers.CharField(read_only=True)
    submitted_date = serializers.DateField(
        read_only=True, 
        input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    questions = QuestionSerializer(read_only=True,many=True)

    class Meta:
        """
        Meta Info.
        """
        model = question_models.Questionnaire
        fields = (
            'name','submitter','submitted_date','total_questions',
            'questions'
            )
