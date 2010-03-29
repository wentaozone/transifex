# -*- coding: utf-8 -*-
"""
String Level models.
"""
import datetime, hashlib, sys

from django.db import models
from django.utils.translation import ugettext_lazy as _

from projects.models import Project
from languages.models import Language


# State Codes for translations
TRANSLATION_STATE_CHOICES = (
    ('APR', 'Approved'),
    ('FUZ', 'Fuzzy'),
    ('REJ', 'Rejected'),
)


# CORE
##############################################################

class TResource(models.Model):
    """
    A translation resource, equivalent to a PO file, YAML file, string stream etc.
    """
    name = models.CharField(_('Name'), max_length=255, null=False,
        blank=False, 
        help_text=_('A descriptive name unique inside the project.'))
    # URI, filepath etc.
    path = models.CharField(_('Path'), max_length=255, null=False,
        blank=False, 
        help_text=_("A path to the template file or to the source stream "
                    "inside the project folders hierarchy or a URI."))
    # Short identifier to be used in the API URLs
#    slug = models.SlugField(_('Slug'), max_length=50,
#        help_text=_('A short label to be used in the URL, containing only '
#                    'letters, numbers, underscores or hyphens.'))

    # Timestamps
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_update = models.DateTimeField(auto_now=True, editable=False)

    # Foreign Keys
    project = models.ForeignKey(Project, verbose_name=_('Project'),
        blank=False, null=True,
        help_text=_("The project which owns the translation resource."))
    source_language = models.ForeignKey(Language,
        verbose_name=_('Source Language'),blank=False, null=True,
        help_text=_("The source language of the translation resource."))

    #TODO: Managers
#    factory = TResourceFactory()

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'project'), 
                           #('slug', 'project'),
                           ('path', 'project'))
        verbose_name = _('tresource')
        verbose_name_plural = _('tresources')
        ordering  = ['name',]
        order_with_respect_to = 'project'
        get_latest_by = 'created'


class SourceString(models.Model):
    """
    A representation of a source string which is translated in many languages.
    
    The SourceString is pointing to a specific TResource and it is uniquely 
    defined by the string, description and tresource fields (so they are unique
    together).
    """

    string = models.CharField(_('String'), max_length=255,
        blank=False, null=False,
        help_text=_("The actual string content of source string."))
    description = models.CharField(_('Description'), max_length=255,
        blank=False, null=False,
        help_text=_("A description of the source string. This field specifies"
                    "the context of the source string inside the tresource."))
    position = models.IntegerField(_('Position'), blank=True, null=True,
        help_text=_("The position of the source string in the TResource."
                    "For example, the specific position of msgid field in a "
                    "po template (.pot) file in gettext."))
    #TODO: Decision for the following
    occurrences = models.TextField(_('Occurrences'), max_length=1000,
        blank=True, editable=False,
        help_text=_("The occurrences of the source string in the project code."))
    flags = models.TextField(_('Flags'), max_length=100,
        blank=True, editable=False,
        help_text=_("The flags which mark the source string. For example, if"
                    "there is a python formatted string this is marked as "
                    "\"#, python-format\" in gettext."))

    # Timestamps
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_update = models.DateTimeField(auto_now=True, editable=False)

    # Foreign Keys
    # A source string must always belong to a tresource
    tresource = models.ForeignKey(TResource, verbose_name=_('TResource'),
        blank=False, null=False,
        help_text=_("The translation resource which owns the source string."))
    language = models.ForeignKey(Language,
        verbose_name=_('Source Language'),blank=False, null=True,
        help_text=_("The source language of the translation resource."))

    #TODO: Managers
#    factory = SourceStringFactory()

    def __unicode__(self):
        return self.string

    class Meta:
        unique_together = (('string', 'description', 'tresource'),)
        verbose_name = _('source string')
        verbose_name_plural = _('source strings')
        ordering  = ['string', 'description']
        order_with_respect_to = 'tresource'
        get_latest_by = 'created'


class TranslationString(models.Model):
    """
    The representation of a live translation for a given source string.
    
    This model encapsulates all the necessary fields for the translation of a 
    source string in a specific target language. It also contains a set of meta
    fields for the context of this translation.
    """

    string = models.CharField(_('String'), max_length=255,
        blank=False, null=False,
        help_text=_("The actual string content of translation."))

    # Timestamps
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_update = models.DateTimeField(auto_now=True, editable=False)

    # Foreign Keys
    # A source string must always belong to a tresource
    source_string = models.ForeignKey(SourceString,
        verbose_name=_('Source String'),
        blank=False, null=False,
        help_text=_("The source string which is being translated by this"
                    "translation string instance."))
    language = models.ForeignKey(Language,
        verbose_name=_('Target Language'),blank=False, null=True,
        help_text=_("The language in which this translation string belongs to."))

    #TODO: Managers
#    factory = SourceStringFactory()

    def __unicode__(self):
        return self.string

    class Meta:
        unique_together = (('string', 'source_string'),)
        verbose_name = _('translation string')
        verbose_name_plural = _('translation strings')
        ordering  = ['string',]
        order_with_respect_to = 'source_string'
        get_latest_by = 'created'
