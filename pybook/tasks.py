from celery import shared_task


@shared_task(ignore_result=True)
def update_recommended_authors(authors, username):
    pass