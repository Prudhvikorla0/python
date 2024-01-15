from modeltranslation.translator import translator, TranslationOptions
from v1.claims import models as claim_models

"""
As per the Translation option class registered
each model will create a migration , which will be 
invisible in the models.py but shall be reflected in the 
migrations:

Any change made in this translation.py file will be 
reflected on the next makemigration

It is suggested to not use inheritance of options class 
and to create individual option field classes and to be 
passed with each models when registering to translate
"""


class ClaimTranslateFields(TranslationOptions):
    fields = ('name', 'description',)


class CriterionTranslateFields(TranslationOptions):
    fields = ('name', 'description',)


translator.register(claim_models.Claim, ClaimTranslateFields)
translator.register(claim_models.Criterion, CriterionTranslateFields)
