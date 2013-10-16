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

import hashlib

from django.template.base import TemplateDoesNotExist
from django.template.loaders.cached import Loader as CachedLoader
from django.template.loader import get_template_from_string, make_origin
from django.utils.encoding import force_bytes


class Loader(CachedLoader):

    def find_template(self, name, dirs=None):
        skip_template = getattr(name, 'skip_template', None)
        needs_smart_extends = skip_template and skip_template.loadname == name
        found_template_loader = False
        for loader in self.loaders:
            if needs_smart_extends and not found_template_loader:
                if hasattr(loader, 'load_template_source'):
                    if (hasattr(skip_template.loader, '__self__') and
                       skip_template.loader.__self__.__class__ == loader.__class__):
                        found_template_loader = True
                else:  # old way to do template loaders
                    found_template_loader = skip_template.loader == loader
                continue
            try:
                template, display_name = loader(name, dirs)
                return (template, make_origin(display_name, loader, name, dirs))
            except TemplateDoesNotExist:
                pass
        raise TemplateDoesNotExist(name)

    def load_template(self, template_name, template_dirs=None):
        key = template_name
        if template_dirs:
            # If template directories were specified, use a hash to differentiate
            key = '-'.join([template_name, hashlib.sha1(force_bytes('|'.join(template_dirs))).hexdigest()])
        if hasattr(template_name, 'skip_template'):
            skip_loader = template_name.skip_template.loader
            if hasattr(skip_loader, '__self__'):
                key = key + '-' + str(template_name.skip_template.loader.__self__.__class__)
            else:
                key = key + '-' + skip_loader.__module__ + '.' + skip_loader.__name__
        if key not in self.template_cache:
            template, origin = self.find_template(template_name, template_dirs)
            if not hasattr(template, 'render'):
                try:
                    template = get_template_from_string(template, origin, template_name)
                except TemplateDoesNotExist:
                    # If compiling the template we found raises TemplateDoesNotExist,
                    # back off to returning the source and display name for the template
                    # we were asked to load. This allows for correct identification (later)
                    # of the actual template that does not exist.
                    return template, origin
            self.template_cache[key] = template
        return self.template_cache[key], None
