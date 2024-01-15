import json
import requests

from django.conf import settings


class ROAIBaseAPI:
    """
    Base class for defining APIs to connect to the RightOrigins AI Module
    """
    base_url: str = settings.ROAI_BASE_URL
    path = "/"
    method = "GET"

    def __init__(self):
        self.headers = {
            'Bearer': settings.ROAI_BEARER_TOKEN,
            'Client-ID': settings.ROAI_CLIENT_ID,
            'Content-Type': 'application/json'
        }
        self.body = {}
        self.url = self.base_url + self.path

    def call(self, **kwargs):

        response = requests.request(
            method=self.method, url=self.url, params=kwargs,
            headers=self.headers, json=self.body, data=json.dumps(self.body)
        ).json()

        if 'data' in response:
            return response['data']
        if 'results' in response:
            return response['results']
        return response
        # raise ValueError("Invalid API response")


class NodeAPI(ROAIBaseAPI):
    """
    API to create a new node in the RO-AI Module.
    """

    path = "data/actor/"
    method = "POST"

    def __init__(self, node_data, ro_number=None):
        super(NodeAPI, self).__init__() # TODO: Super added into first from last
        self.ro_number = ro_number
        self.body = node_data
        # method = "patch" if self.ro_number else self.method  TODO: Uncomment this when patch is added in AI Module


class GetScore(ROAIBaseAPI):
    """
    API to get score of a node based on its ro_number
    """

    path = "data/{ro_number}/"
    method = "GET"

    def __init__(self, ro_number):
        self.ro_number = ro_number
        self.path = self.path.format(ro_number=ro_number) # TODO: Path issue fixed.
        super(GetScore, self).__init__()


class GetRecommendedStandards(ROAIBaseAPI):
    """
    API to get list of recommended cetifications
    """

    path = "data/{ro_number}/standards/"
    method = "GET"

    def __init__(self, ro_number):
        self.ro_number = ro_number
        self.path = self.path.format(ro_number=ro_number)
        super(GetRecommendedStandards, self).__init__()


class GetAllStandards(ROAIBaseAPI):
    """
    API to get list of all standards
    """

    path = "data/standards/"
    method = "GET"


class AddStandard(ROAIBaseAPI):
    """
    API to create a new node in the RO-AI Module.
    """

    path = "data/certification/"
    method = "POST"

    def __init__(self, node_claim):
        super(AddStandard, self).__init__() # TODO: super moved to here.
        self.ro_number = node_claim.node.ro_number
        self.body = {
            "actor": node_claim.node.ro_number,
            "standard": node_claim.claim.standard_id,
            "anniversary_date": node_claim.expiry_date.strftime('%Y-%m-%d')
        }


class GetAddedCertificates(ROAIBaseAPI):
    """
    API to list certificates added to node in RO-AI module
    """

    path = "data/{ro_number}/"
    method = "GET"

    def __init__(self, ro_number):
        self.ro_number = ro_number
        self.path = self.path.format(ro_number=ro_number)
        super(GetAddedCertificates, self).__init__()


class NodeSearch(ROAIBaseAPI):
    """
    API to list nodes.
    """

    path = "data/actor/search/"
    method = "GET"

    def __init__(self):
        super(NodeSearch, self).__init__()


class CountryList(ROAIBaseAPI):
    """
    API to list nodes.
    """

    path = "data/country/"
    method = "GET"
