import time

from django.conf import settings

from v1.questionnaire.tasks import client


def get_answer_openai(question):

    assistant = client.beta.assistants.retrieve(settings.OPEN_AI_ASSISTANT_ID)
    thread = client.beta.threads.create()
    _ = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question)
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=".")

    for c in range(30):
        if run.status == 'completed':
            break
        if run.status == 'failed':
            return "Could not fetch answer"
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(run.id, thread_id=thread.id)

    messages = client.beta.threads.messages.list(
        thread_id=thread.id)
    for data in messages.data:
        for content in data.content:
            if content.text.value and content.text.value != question:
                # print(content.text.value)
                return content.text.value
    return ""
