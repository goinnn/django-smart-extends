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
from django.template.loader import template_source_loaders, make_origin


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
            if hasattr(template_source_loader, 'load_template_source'):
                if (hasattr(skip_template.loader, '__self__') and
                   skip_template.loader.__self__.__class__ == template_source_loader.__class__):
                    tsl_index = i
            else:  # old way to do template loaders
                if skip_template.loader == template_source_loader:
                    tsl_index = i

            if tsl_index != -1:
                break
    for loader in template_source_loaders[tsl_index + 1:]:
        try:
            source, display_name = loader(name, dirs)
            return (source, make_origin(display_name, loader, name, dirs))
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist(name)
