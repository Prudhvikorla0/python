from v1.risk.integrations.roai.apis import GetAllStandards
from v1.claims.models import Claim, NodeClaim
from v1.claims.constants import ClaimType, ClaimAddedBy, ClaimStatus

from django.utils import timezone


def sync_standard_from_roai(tenant, update_existing=False):
    not_updated = 0
    for claim_data in GetAllStandards().call(limit=500):
        claim_key = claim_data.pop('key')
        claim_dict = {
            'name': claim_data['name'],
            'description': claim_data['description'],
            'standard_id': claim_data['id'],

            'tenant': tenant,
            'attach_to_node': True,
            'attach_from_profile': True,
            'attach_while_connecting': True,
            'attach_to_batch': False,
            'attach_from_batch_details': False,
            'attach_while_transacting': False,
            'type': ClaimType.COMPANY_CLAIM, 
            'added_by': ClaimAddedBy.RO_AI
        }
        print(f"Adding standard : {claim_dict['name']}")

        claim, created = Claim.objects.get_or_create(
            code=claim_key, defaults=claim_dict)
        if not created:
            if not update_existing:
                print(f"~ Standard {claim_dict['name']} exists. Skipping")
                not_updated += 1
                continue
            print(f"# Standard {claim_dict['name']} exists. Updating")
            for k, v in claim_dict:
                setattr(claim, k, v)
            claim.save()
    if not update_existing and not_updated:
        print(f"!!!!!!! {not_updated} standards were already present and were not updated.")


def expire_claims(tenant=None):
    """
    Expires claims.
    """
    today = timezone.datetime.now().date()
    NodeClaim.objects.exclude(
        expiry_date=None).filter(node__tenant=tenant,expiry_date__lt=today).update(
            status=ClaimStatus.EXPIRED)
