"""
Celery tasks
"""
import logging
import openai
from celery import shared_task

from django.conf import settings

from v1.questionnaire.openai_utils.find_answers import get_answer_openai

from . import models as ques_models
from . import constants

logger = logging.getLogger(__name__)
client = openai.OpenAI(api_key=settings.OPEN_AI_API_KEY)


@shared_task(name='find_answer')
def find_answer(question_id: int,extra_data=None):
    """Function to find answers to the questions in the questionnaire."""
    question = ques_models.Question.objects.get(id=question_id)
    answer = get_answer_openai(question.question)

    answer_obj = ques_models.Answer.objects.create(
        question=question, answer=answer, type=constants.AnswerType.AUTOMATIC)

    return True

