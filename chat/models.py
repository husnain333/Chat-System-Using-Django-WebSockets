from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    name = models.CharField(_('name'), max_length=64)
    email_address = models.EmailField(_('email address'))
    homepage = models.URLField(_('home page'), blank=True)
    comment = models.TextField(_('comment'))
    pub_date = models.DateTimeField(_('Published date'), auto_now_add=True)
    is_spam = models.BooleanField(_('spam?'), default=False)

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')