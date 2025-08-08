from celery import shared_task, group
import chatproject
from chatproject.celery import app
from chat.models import Message, ChatRoom
import json
from django.core import serializers
from django.contrib.auth.models import User
from akismet import Akismet
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site
from .models import Comment
from django.core.mail import send_mail
import logging
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)

@shared_task
def taskEveryHour():
    logger.info("Running taskEveryHour")
    
@shared_task
def weekelySummary():
    oneWeek = datetime.now() - timedelta(days=7)
    users = User.objects.filter(is_active=True)
    for user in users:
        activity_count = 5
        send_mail(
            subject="Your Weekly Summary",
            message=f"{user.username},\nYou had {activity_count} activities this week.",
            from_email="no-reply@example.com",
            recipient_list=[user.email],
        )
    return f"Sent weekly summary to {users.count()} users."

@shared_task
def confirmationEmail(email, username):
    subject = "Confirmation Email"
    message = f'Hi {username},\n\nThank you for signing up! \n\nBest regards,\n M Husnain'
    from_email = chatproject.settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


@shared_task
def add(x, y):
    return x + y

@app.task(trail=True)
def A(how_many):
    return group(B.s(i) for i in range(how_many))()

@app.task(trail=True)
def B(i):
    return pow2.delay(i)

@app.task(trail=True)
def pow2(i):
    return i ** 2

@shared_task
def save_messages():
    messages = Message.objects.all()
    rooms = ChatRoom.objects.all()
    data = { 'messages': json.loads(serializers.serialize('json', messages)),
             'rooms': json.loads(serializers.serialize('json', rooms)) } 
    filename = 'messages.json'
    with open(filename, 'w') as f:
        json.dump(data, f)

    return f"Data Saved to file: {filename}"

@shared_task
def backup_users():
    Users = User.objects.all()

    data = json.loads(serializers.serialize('json', Users))
    filename = 'users.json'
    with open(filename, 'w') as f:
        json.dump(data, f)
    return f"Users Data Saved to file: {filename}"

@app.task
def spam_filter(comment_id, remote_addr=None):
    logger = spam_filter.get_logger()
    logger.info('Running spam filter for comment %s', comment_id)

    comment = Comment.objects.get(pk=comment_id)
    current_domain = Site.objects.get_current().domain
    akismet = Akismet(chatproject.settings.AKISMET_KEY, 'http://{0}'.format(current_domain))
    if not akismet.verify_key():
        raise ImproperlyConfigured('Invalid AKISMET_KEY')


    is_spam = akismet.comment_check(user_ip=remote_addr,
                        comment_content=comment.comment,
                        comment_author=comment.name,
                        comment_author_email=comment.email_address)
    if is_spam:
        comment.is_spam = True
        comment.save()

    return is_spam