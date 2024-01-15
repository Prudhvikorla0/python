from django.contrib import admin

from common.admin import BaseAdmin

from v1.questionnaire import models as question_models


class Answerline(admin.TabularInline):
    """In-line view function for Sub-element model."""

    model = question_models.Answer
    extra = 0
    fields = ('answer','files','is_deleted',)

class Questionline(admin.TabularInline):
    """In-line view function for Sub-element model."""

    inlines = [Answerline]
    model = question_models.Question
    extra = 0
    fields = ('question','is_deleted')

class QuestionnaireAdmin(BaseAdmin):
    """Class view to customize view of questionnaire."""

    list_display = ('name', 'owner', 'submitter', 'status', 'idencode')
    inlines = [
        Questionline,
    ]
    list_filter = ('is_deleted', 'status',)
    search_fields = ['name']


class QuestionAdmin(BaseAdmin):
    """Class view to customize view of question."""

    list_display = ('question', 'questionnaire','idencode')
    inlines = [
        Answerline,
    ]
    list_filter = ('is_deleted',)
    search_fields = ['question',]

class AnswerAdmin(BaseAdmin):
    """Class view to customize view of answer."""

    list_display = ('answer','question','idencode')
    list_filter = ('is_deleted',)
    search_fields = ['answer',]

admin.site.register(question_models.Questionnaire,QuestionnaireAdmin)
admin.site.register(question_models.Question,QuestionAdmin)
admin.site.register(question_models.Answer,AnswerAdmin)
