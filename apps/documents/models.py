import errno
import os
import uuid
import mimetypes
from datetime import datetime

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from dynamic_search.api import register

from documents.conf.settings import AVAILABLE_FUNCTIONS
from documents.conf.settings import FILESERVING_PATH
from documents.conf.settings import SLUGIFY_PATH

if SLUGIFY_PATH == False:
    #Do not slugify path or filenames and extensions
    slugify = lambda x:x


def get_filename_from_uuid(instance, filename, directory='documents'):
    populate_file_extension_and_mimetype(instance, filename)
    stem, extension = os.path.splitext(filename)
    return '%s/%s%s' % (directory, instance.uuid, extension)

def populate_file_extension_and_mimetype(instance, filename):
    # First populate the file extension and mimetype
    instance.file_mimetype, encoding = mimetypes.guess_type(filename) or ""
    instance.file_filename, instance.file_extension = os.path.splitext(filename)

class DocumentType(models.Model):
    name = models.CharField(max_length=32, verbose_name=_(u'name'))    
    
    def __unicode__(self):
        return self.name
        
        
class Document(models.Model):
    """ Minimum fields for a document entry.
        Inherit this model to customise document metadata, see BasicDocument for an example.
    """
    document_type = models.ForeignKey(DocumentType, verbose_name=_(u'document type'))
    file = models.FileField(upload_to=get_filename_from_uuid)#lambda i,f: 'documents/%s' % i.uuid)
    uuid = models.CharField(max_length=36, default=lambda:unicode(uuid.uuid4()), blank=True, editable=False)
    file_mimetype = models.CharField(max_length=50, default="", editable=False)
    file_filename = models.CharField(max_length=64, default="", editable=False)
    file_extension = models.CharField(max_length=10, default="", editable=False)
    date_added = models.DateTimeField("added", auto_now_add=True)
    date_updated = models.DateTimeField("updated", auto_now=True)
    
    class Meta:
        verbose_name = _(u'document')
        verbose_name_plural = _(u'documents')
        ordering = ['-date_updated', '-date_added']
        
    def __unicode__(self):
        return self.uuid
        
    @models.permalink
    def get_absolute_url(self):
        return ('document_view', [self.id])

    def create_fs_links(self):
        for metadata in self.documentmetadata_set.all():
            if metadata.metadata_type.documenttypemetadatatype_set.all()[0].create_directory_link:
                target_directory = os.path.join(FILESERVING_PATH, slugify(metadata.metadata_type.name), slugify(metadata.value))
                try:
                    os.makedirs(target_directory)
                except OSError as exc:
                    if exc.errno == errno.EEXIST:
                        pass
                    else: 
                        raise 'Unable to create metadata indexing directory.'

                if SLUGIFY_PATH:
                    extsep = os.extsep
                else:
                    extsep = ''
                    
                target_filepath = os.path.join(target_directory, extsep.join([slugify(self.file_filename), slugify(self.file_extension)]))
                    
                try:
                    os.symlink(os.path.abspath(self.file.path), target_filepath)
                except OSError as exc:
                    if exc.errno == errno.EEXIST:
                        pass
                    else: 
                        raise 'Unable to create metadata indexing directory.'


available_functions_string = (_(u' Available functions: %s') % ','.join(['%s()' % name for name, function in AVAILABLE_FUNCTIONS.items()])) if AVAILABLE_FUNCTIONS else ''

class MetadataType(models.Model):
    name = models.CharField(max_length=32, verbose_name=_(u'name'))
    default = models.CharField(max_length=64, blank=True, null=True,
        verbose_name=_(u'default'), help_text=_(u'Enter a string to be evaluated.%s') % available_functions_string)
    lookup = models.CharField(max_length=64, blank=True, null=True, verbose_name=_(u'lookup'))
    #datatype = models.
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        verbose_name = _(u'metadata type')
        verbose_name_plural = _(u'metadata types')


class DocumentTypeMetadataType(models.Model):
    document_type = models.ForeignKey(DocumentType, verbose_name=_(u'document type'))
    metadata_type = models.ForeignKey(MetadataType, verbose_name=_(u'metadata type'))
    create_directory_link = models.BooleanField(verbose_name=_(u'create directory link'))
    #override default
    #required? -bool
    
    def __unicode__(self):
        return unicode(self.metadata_type)

    class Meta:
        verbose_name = _(u'document type metadata type connector')
        verbose_name_plural = _(u'document type metadata type connectors')


class DocumentMetadata(models.Model):
    document = models.ForeignKey(Document, verbose_name=_(u'document'))
    metadata_type = models.ForeignKey(MetadataType, verbose_name=_(u'metadata type'))
    value = models.TextField(blank=True, null=True, verbose_name=_(u'metadata value'))
 
    def __unicode__(self):
        return unicode(self.metadata_type)

    class Meta:
        verbose_name = _(u'document metadata')
        verbose_name_plural = _(u'document metadata')


register(Document, _(u'document'), ['document_type__name', 'file_mimetype', 'file_filename', 'file_extension'])
