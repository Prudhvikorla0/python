"""
Celery tasks
"""
import time
import traceback
import logging
import copy
from sentry_sdk import capture_exception
from celery import shared_task

from django.conf import settings

from utilities import functions

from v1.supply_chains.serializers import connections
from v1.transactions.serializers import external

from . import models as bulk_models
from . import constants


logger = logging.getLogger(__name__)


@shared_task(name='upload')
def upload(upload_id: int,extra_data=None):
    """Function to create Validator email."""
    bulk_upload = bulk_models.BulkUpload.objects.get(id=upload_id)
    bulk_upload.status = constants.BulkUploadStatuses.IN_PROGRESS
    for item in bulk_upload.validated_data:
        item['data']['_status'] = {
            "value": constants.BulkUploadStatuses.IN_PROGRESS,
            "message": "",
            "is_valid": True,
            "hidden": True,
        }
    bulk_upload.save()
    config_class = constants.TemplateType(bulk_upload.template.type).function()
    for item in bulk_upload.validated_data:
        item_data = item['data']
        # serializer_data = copy.deepcopy(item)
        serializer_data = {k: v['value'] for k, v in item_data.items()}
        serializer_data = config_class.annotate_extras(serializer_data)
        serializer_data['current_tenant'] = bulk_upload.tenant
        serializer_data['current_node'] = bulk_upload.node
        serializer_data['current_user'] = bulk_upload.creator
        if serializer_data['_status'] in [
                constants.BulkUploadStatuses.COMPLETED,
                constants.BulkUploadStatuses.FAILED]:
            continue
        serializer_data['supply_chain'] = bulk_upload.supply_chain.idencode
        if extra_data:
            for key,value in extra_data.items():
                serializer_data[key] = value
        instance = config_class.get_instance(serializer_data)
        serializer_class = config_class.get_serializer_class(instance)
        serializer = serializer_class(instance=instance, data=serializer_data, partial=True)

        try:
            if serializer.is_valid():
                serializer.save()
                item_data['_status']['value'] = constants.BulkUploadStatuses.COMPLETED
                if instance:
                    bulk_upload.updations_completed += 1
                else:
                    bulk_upload.new_items_completed += 1
            else:
                item_data['_status']['value'] = constants.BulkUploadStatuses.FAILED
                item['errors'] = serializer.errors
                bulk_upload.errors.append(serializer.errors)
                if instance:
                    bulk_upload.updations_failed += 1
                else:
                    bulk_upload.new_items_failed += 1
        except Exception as e:
            err = traceback.format_exc()
            capture_exception(e)
            item_data['_status']['value'] = constants.BulkUploadStatuses.FAILED
            item['errors'] = [str(err)]
            bulk_upload.errors.append(str(err))
            if instance:
                bulk_upload.updations_failed += 1
            else:
                bulk_upload.new_items_failed += 1
        bulk_upload.save()
        time.sleep(1)
    if bulk_upload.errors:
        bulk_upload.status = constants.BulkUploadStatuses.FAILED
    else:
        bulk_upload.status = constants.BulkUploadStatuses.COMPLETED
    bulk_upload.save()
    bulk_upload.notify()
    return True

