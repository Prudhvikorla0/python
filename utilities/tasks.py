from celery import shared_task
from sentry_sdk import capture_message

from utilities import calculate_risk

from v1.risk.integrations.roai import apis as roai_apis

from v1.tenants.models import Country,Tenant

from v1.claims import utilities as claim_utilities


@shared_task(name='update_country_score')
def update_country_score():
    """
    Fn to update country score.
    """
    roai_countries = roai_apis.CountryList().call(limit=1000)
    for roai_country in roai_countries:
        try:
            country = Country.objects.get(
                alpha_3__iexact=roai_country['code'])
        except:
            continue
        country.score = roai_country['score']
        country.save()
    capture_message("Country Scores Updated Successfully")

@shared_task(name='update_sc_risk_score')
def update_sc_risk_score():
    """
    Fn to update supplychain risk score of each connections.
    """
    tenants = Tenant.objects.all()
    for tenant in tenants:
        try:
            calculate_risk.UpdateScore().update_sc_score(tenant)
        except:
            continue
    capture_message("SupplyChain Scores Updated Successfully")

@shared_task(name='sync_roai_standards')
def sync_roai_standards():
    """
    Fn to sync standard from ro-ai to each tenants.
    """
    tenants = Tenant.objects.all()
    for tenant in tenants:
        try:
            claim_utilities.sync_standard_from_roai(
                tenant, update_existing=True)
        except:
            pass
    capture_message("ROAI Standards Updated Successfully")
