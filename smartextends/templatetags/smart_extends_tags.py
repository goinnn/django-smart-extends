# Copyright (c) 2010-2013 by Pablo Martin <goinnn@gmail.com>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

from django.template import TemplateSyntaxError
from django.template import Library
from django.conf import settings
from django.template.base import Variable
from django.template.loader_tags import ExtendsNode

from smartextends.loader import get_template

register = Library()


class SmartExtendsNode(ExtendsNode):

    def __repr__(self):
        return '<SmartExtendsNode: extends %s>' % self.parent_name.token

    def get_parent(self, context):
        parent = self.parent_name.resolve(context)
        if not parent:
            error_msg = "Invalid template name in 'extends' tag: %r." % parent
            if self.parent_name.filters or\
                    isinstance(self.parent_name.var, Variable):
                error_msg += " Got this from the '%s' variable." % self.parent_name.token
            raise TemplateSyntaxError(error_msg)
        if hasattr(parent, 'render'):
            return parent  # parent is a Template object
        origin, source = self.source
        return get_template(parent, skip_template=origin)


def do_smart_extends(parser, token):
    """
    Signal that this template smart_extends a parent template.

    This tag may be used similarly to extends (django tag).
    This tag provides the possibility to extend to yourself without infinite
    recursion. It is possible for use a API function "find_template",
    that skip the invoke template
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes one argument" % bits[0])
    parent_name = parser.compile_filter(bits[1])
    nodelist = parser.parse()
    if nodelist.get_nodes_by_type(SmartExtendsNode):
        raise TemplateSyntaxError("'%s' cannot appear more than once in the same template" % bits[0])
    return SmartExtendsNode(nodelist, parent_name)


if getattr(settings, 'OVERWRITE_EXTENDS', False):
    register.tag('extends', do_smart_extends)
register.tag('smart_extends', do_smart_extends)
