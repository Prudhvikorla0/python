"""URLs of the app supply-chains."""

from rest_framework import routers
from django.urls import path,include

from v1.questionnaire import views as question_views
from v1.questionnaire import models as question_models


router = routers.SimpleRouter()

router.register(
    r'questions', question_views.QuestionViewSet,
    basename=question_models.Question)
router.register(
    r'', question_views.QuestionnaireViewSet,
    basename=question_models.Questionnaire)

urlpatterns = router.urls

urlpatterns += [
    path('submitter/list/', 
         question_views.QuestionnaireSubmitterListView.as_view(),
         name='questionnaire-submitters-list'),
    path('<idencode:pk>:approve', 
         question_views.QuestionnaireApproveView.as_view(),
         name='questionnaire-approve'),
    
    path('questions/<idencode:pk>/answer/', 
         question_views.AnswerCreateUpdateView.as_view(),
         name='answer-create'),
    path('questions/<idencode:pk>/answer/<idencode:id>/', 
         question_views.AnswerCreateUpdateView.as_view(),
         name='answer-update'),
    path('<idencode:pk>/public/', 
         question_views.PublicQuestionnaireView.as_view(),
         name='public-questionnaire-info'),
    path('<idencode:pk>/share/', 
         question_views.ShareQuestionnaire.as_view(),
         name='share-questionnaire-info'),
    path('<idencode:pk>/link/', 
         question_views.CreateLink.as_view(),
         name='create-questionnaire-link'),
    path('check/availability/', 
         question_views.CheckQuestionnaireAvailability.as_view(),
         name='check-questionnaire-availabilty'),
]
