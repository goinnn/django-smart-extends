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

from django.conf import settings

from django.template import TemplateDoesNotExist
from django.template.loader import get_template_from_string
from django.template.loader import make_origin
from django.template.loaders.cached import Loader as CachedLoader


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
    from django.template.loader import template_source_loaders
    # Calculate template_source_loaders the first time the function is executed
    # because putting this logic in the module-level namespace may cause
    # circular import errors. See Django ticket #1292.
    global template_source_loaders
    if template_source_loaders is None:
        loaders = []
        template_loaders = settings.TEMPLATE_LOADERS
        for loader_name in template_loaders:
            loader = find_template_loader(loader_name)
            if loader is not None:
                loaders.append(loader)
        template_source_loaders = tuple(loaders)
    setattr(name, 'skip_template', skip_template)
    needs_smart_extends = skip_template.loadname == name
    found_template_loader = False
    for loader in template_source_loaders:
        if needs_smart_extends and not found_template_loader and not isinstance(loader, CachedLoader):
            if hasattr(loader, 'load_template_source'):
                if (hasattr(skip_template.loader, '__self__') and
                   skip_template.loader.__self__.__class__ == loader.__class__):
                    found_template_loader = True
            else:  # old way to do template loaders
                found_template_loader = skip_template.loader == loader
            continue
        try:
            source, display_name = loader(name, dirs)
            return (source, make_origin(display_name, loader, name, dirs))
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist(name)
