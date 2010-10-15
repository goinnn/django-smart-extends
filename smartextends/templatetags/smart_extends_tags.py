import django
from django.template import TemplateSyntaxError, TemplateDoesNotExist
from django.template import Library
from django.conf import settings
from django.template.loader import get_template_from_string
from django.template.loader import template_source_loaders, make_origin
from django.template.loader_tags import ExtendsNode
from django.utils.importlib import import_module

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

def get_source(source):
    if getattr(source, '__iter__', None):
        source = source[0]
    return source

def find_template(name, dirs=None, skip_template=None):
    from django.template.loader import find_template_loader
    # Calculate template_source_loaders the first time the function is executed
    # because putting this logic in the module-level namespace may cause
    # circular import errors. See Django ticket #1292.
    global template_source_loaders
    if template_source_loaders is None:
        loaders = []
        for loader_name in settings.TEMPLATE_LOADERS:
            loader = find_template_loader(loader_name)
            if loader is not None:
                loaders.append(loader)
        template_source_loaders = tuple(loaders)
    template_candidate = None
    for loader in template_source_loaders:
        try:
            source, display_name = loader(name, dirs)
            if skip_template:
                extends_tags = source.nodelist[0]
                if get_source(extends_tags.source).name == skip_template.name:
                    template_candidate = None
                    continue
                if not template_candidate:
                    template_candidate = (source, make_origin(display_name, loader, name, dirs))
            else:
                return (source, make_origin(display_name, loader, name, dirs))
        except TemplateDoesNotExist:
            pass
    if not template_candidate:
        raise TemplateDoesNotExist(name)
    return template_candidate


class SmartExtendsNode(ExtendsNode):

    def __repr__(self):
        if self.parent_name_expr:
            return "<SmartExtendsNode: extends %s>" % self.parent_name_expr.token
        return '<SmartExtendsNode: extends "%s">' % self.parent_name

    def get_source(self):
        source = getattr(self, 'source', None)
        return get_source(source)

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
            return parent # parent is a Template object
        source = self.get_source()
        return get_template(parent, skip_template=source)

    def render(self, context):
        source = self.get_source()
        if source and source.loadname == self.parent_name:
            template = find_template(self.parent_name, skip_template=source)
            template_source = template[0]
            extends_tags = template_source.nodelist[0]
            self.parent_name = extends_tags.get_source().name
        return super(SmartExtendsNode, self).render(context)


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
