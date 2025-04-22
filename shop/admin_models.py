from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings

class AdminLogEntry(models.Model):
    action_time = models.DateTimeField(
        _('action time'),
        auto_now=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name=_('user'),
        related_name='admin_log_entries',
    )
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name=_('content type'),
        blank=True,
        null=True,
    )
    object_id = models.TextField(_('object id'), blank=True, null=True)
    object_repr = models.CharField(_('object repr'), max_length=200)
    action_flag = models.PositiveSmallIntegerField(_('action flag'))
    change_message = models.TextField(_('change message'), blank=True)

    class Meta:
        verbose_name = _('admin log entry')
        verbose_name_plural = _('admin log entries')
        db_table = 'admin_log_entry'
        ordering = ['-action_time']

    def __str__(self):
        return f'{self.action_time} - {self.user} - {self.object_repr}' 