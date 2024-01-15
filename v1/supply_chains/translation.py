from modeltranslation.translator import translator, TranslationOptions
from v1.supply_chains import models as sc_models

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


class OperationTranslateFields(TranslationOptions):
    fields = ('name',)


class SupplychainTranslateFields(TranslationOptions):
    fields = ('name', 'description',)


translator.register(sc_models.Operation, OperationTranslateFields)
translator.register(sc_models.SupplyChain, SupplychainTranslateFields)
