from modeltranslation.translator import translator, TranslationOptions
from v1.tenants import models as tenant_models

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


# class CountryTranslateFields(TranslationOptions):
#     fields = ('name',)


# class ProvinceTranslateFields(TranslationOptions):
#     fields = ('name',)


# class CurrencyTranslateFields(TranslationOptions):
#     fields = ('name',)


class CategoryTranslateFields(TranslationOptions):
    fields = ('name',)


# translator.register(tenant_models.Country, CountryTranslateFields)
# translator.register(tenant_models.Province, ProvinceTranslateFields)
# translator.register(tenant_models.Currency, CurrencyTranslateFields)
translator.register(tenant_models.Category, CategoryTranslateFields)
