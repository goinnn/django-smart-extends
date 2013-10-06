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

from django.template import TemplateSyntaxError, TemplateDoesNotExist
from django.template import Library
from django.conf import settings
from django.template.loader import get_template_from_string
from django.template.loader import template_source_loaders, make_origin
from django.template.loader_tags import ExtendsNode

register = Library()


def get_template(template_name, skip_template=None):
    """
    Returns a compiled Template object for the given template name,
    handling template inheritance recursively.
    """
    template, origin = find_template(template_name, skip_template=skip_template)
    if not hasattr(template, 'render'):
        # template needs to be compiled
        template = get_template_from_string(template, origin, template_name)
    return template


def find_template(name, dirs=None, skip_template=None):
    """
    Returns a tuple with a compiled Template object for the given template name,
    and a origin object. Skipping the current template (skip_template),
    this param contain the absolute path of the template.
    """
    from django.template.loader import find_template_loader
    # Calculate template_source_loaders the first time the function is executed
    # because putting this logic in the module-level namespace may cause
    # circular import errors. See Django ticket #1292.
    global template_source_loaders
    if template_source_loaders is None:
        loaders = []
        template_loaders = settings.TEMPLATE_LOADERS
        if isinstance(template_loaders[0], tuple) or isinstance(template_loaders[0], list):
            # django.template.loaders.cached.Loader. See template caching in Django docs
            template_loaders = template_loaders[0][1]
        for loader_name in template_loaders:
            loader = find_template_loader(loader_name)
            if loader is not None:
                loaders.append(loader)
        template_source_loaders = tuple(loaders)
    tsl_index = -1
    if skip_template and skip_template.loadname == name:
        for i, template_source_loader in enumerate(template_source_loaders):
            if isinstance(skip_template.loader.__self__, template_source_loader.__class__):
                tsl_index = i
                break
    for loader in template_source_loaders[tsl_index + 1:]:
        try:
            source, display_name = loader(name, dirs)
            return (source, make_origin(display_name, loader, name, dirs))
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist(name)


class SmartExtendsNode(ExtendsNode):

    def __repr__(self):
        if self.parent_name_expr:
            return "<SmartExtendsNode: extends %s>" % self.parent_name_expr.token
        return '<SmartExtendsNode: extends "%s">' % self.parent_name

    def get_parent(self, context):
        if self.parent_name_expr:
            self.parent_name = self.parent_name_expr.resolve(context)
        parent = self.parent_name
        if not parent:
            error_msg = "Invalid template name in 'extends' tag: %r." % parent
            if self.parent_name_expr:
                error_msg += " Got this from the '%s' variable." % self.parent_name_expr.token
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
    parent_name, parent_name_expr = None, None
    if bits[1][0] in ('"', "'") and bits[1][-1] == bits[1][0]:
        parent_name = bits[1][1:-1]
    else:
        parent_name_expr = parser.compile_filter(bits[1])
    nodelist = parser.parse()
    if nodelist.get_nodes_by_type(SmartExtendsNode):
        raise TemplateSyntaxError("'%s' cannot appear more than once in the same template" % bits[0])
    return SmartExtendsNode(nodelist, parent_name, parent_name_expr)


if getattr(settings, 'OVERWRITE_EXTENDS', False):
    register.tag('extends', do_smart_extends)
register.tag('smart_extends', do_smart_extends)
