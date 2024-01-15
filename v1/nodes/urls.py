"""URLs of the app accounts."""

from rest_framework import routers

from django.urls import path

from v1.nodes.views import node as node_viewset
from v1.nodes import models as node_models
from v1.nodes.views import folder as folder_viewset


router = routers.SimpleRouter()

urlpatterns = [
    path('members:resend-invite', node_viewset.ResendNodeMemberInvite.as_view()),
    path('<idencode:pk>/', node_viewset.NodeRetrieveUpdateView.as_view(),
        name='retrieve-update-company'),
    path('search/', node_viewset.SearchNode.as_view(),
        name='search-node'),
    path('ai/search/', node_viewset.ROAINodeSearch.as_view(),
        name='search-node-ai'),
    
]

router.register(r'documents', node_viewset.NodeDocumentViewSet,
    basename=node_models.NodeDocument)
router.register(r'members', node_viewset.NodeMemberViewSet, 
    basename=node_models.NodeMember)
router.register(r'folders', folder_viewset.FolderViewSet, 
    basename=node_models.Folder)

urlpatterns += router.urls
