from django.conf import settings

from bson.objectid import ObjectId


def create_collection(collection=''):
    """
    Function to create collection(table) in mongodb.
    """
    try:
        settings.MONGO_DB.create_collection(name=collection)
    except:
        return False
    return True

def add_single_document(collection='', data={}):
    """
    Function to add single data(row) into the collection(table).
    Function returns created data's unique id.
    """
    collection = settings.MONGO_DB[collection]
    mongo_instance = collection.insert_one(data)
    return mongo_instance.inserted_id

def add_multiple_document(collection='', data=[]):
    """
    Function to add multiple data(row) into the collection(table).
    Function returns created data's unique id.
    Data is passed as list of dictionaries.
    """
    collection = settings.MONGO_DB[collection]
    mongo_instances = collection.insert_many(data)
    return mongo_instances.inserted_ids

def get_single_document(collection='', document_id=None):
    """
    Function returns single document details from given id.
    """
    collection = settings.MONGO_DB[collection]
    document_id = ObjectId(document_id)
    document = collection.find_one({"_id": document_id})
    return document

def search_document(collection='', search_criteria={}):
    """
    Function returns searched documents based on the criteria.
    """
    collection = settings.MONGO_DB[collection]
    documents = list(collection.find(search_criteria))
    return documents

def update_single_document(
        collection='', document_id=None, updated_data={}):
    """
    Function to update a single document.
    """
    collection = settings.MONGO_DB[collection]
    document_id = ObjectId(document_id)
    update_document_data = {
        "$set":updated_data
        }
    updated_document = collection.find_one_and_update(
        {"_id": document_id}, update_document_data, 
        return_document=True)
    return updated_document

def update_multiple_document(criteria={}, updated_data={}):
    """
    Function to update multiple documents based on the criteria.
    """
    collection = settings.MONGO_DB[collection]
    update_document_data = {
        "$set":updated_data
        }
    updated_documents = collection.update_many(
        criteria, update_document_data)
    return updated_documents

def delete_single_document(collection='', document_id=None):
    """
    Function to delete document based on id.
    """
    collection = settings.MONGO_DB[collection]
    document_id = ObjectId(document_id)
    collection.delete_one({"_id": document_id})
    return True

def delete_multiple_document(criteria={}, updated_data={}):
    """
    Function to update multiple documents based on the criteria.
    """
    collection = settings.MONGO_DB[collection]
    collection.delete_many(criteria)
    return True
