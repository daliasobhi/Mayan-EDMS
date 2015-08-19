from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Link

from .permissions import (
    permission_key_delete, permission_key_receive, permission_key_view,
    permission_keyserver_query
)

link_private_keys = Link(
    icon='fa fa-key', permissions=(permission_key_view,),
    text=_('Private keys'), view='django_gpg:key_private_list'
)
link_public_keys = Link(
    icon='fa fa-key', permissions=(permission_key_view,), text=_('Public keys'),
    view='django_gpg:key_public_list'
)
link_key_delete = Link(
    permissions=(permission_key_delete,), tags='dangerous', text=_('Delete'),
    view='django_gpg:key_delete', args=('object.fingerprint', 'object.type',)
)

link_key_query = Link(
    permissions=(permission_keyserver_query,), text=_('Query keyservers'),
    view='django_gpg:key_query'
)
link_key_receive = Link(
    keep_query=True, permissions=(permission_key_receive,), text=_('Download'),
    view='django_gpg:key_receive', args='object.key_id'
)
link_key_setup = Link(
    icon='fa fa-key', permissions=(permission_key_view,),
    text=_('Key management'), view='django_gpg:key_public_list'
)
