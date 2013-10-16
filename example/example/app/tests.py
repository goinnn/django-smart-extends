# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 by Pablo Martín <goinnn@gmail.com>
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
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.base import TemplateSyntaxError, TemplateDoesNotExist
from django.template.loader_tags import do_extends
from django.test import TestCase
from django.test.client import Client

from smartextends.templatetags.smart_extends_tags import do_smart_extends, register

logging.basicConfig()
logger = logging.getLogger('test.app')

INSTALLED_DB_TEMPLATES = ('example.dbtemplates_fixtures' in settings.INSTALLED_APPS and
                          'dbtemplates' in settings.INSTALLED_APPS)

if not INSTALLED_DB_TEMPLATES:
    logger.warning('If you want more complete tests, please install django-dbtemplates (to know the version, see tox.ini file)')


class SmartExtendsCase(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

    def __client_login(self):
        client = self.client
        user = 'admin'
        password = 'testtest'
        is_login = client.login(username=user, password=password)
        self.assertEqual(is_login, True)
        self.user = User.objects.get(username=user)
        return client

    def check_url(self, client, url):
        response = client.get(url)
        str_extension = 'Overwriting the change_form template in our project without to have to copy every line of this template in our project'
        self.assertEqual(str_extension in response.content.decode('utf-8'), True)
        if INSTALLED_DB_TEMPLATES:
            str_extension_db_templates = 'Overwriting the change_form template using '
            self.assertEqual(str_extension_db_templates in response.content.decode('utf-8'), True)

    def check_error(self, client, url, exception):
        try:
            self.check_url(client, url)
            self.assertEqual(False, True)
        except exception:
            pass

    def add_cache_template(self):
        from django.template import loader
        settings.TEMPLATE_LOADERS = (('smartextends.loaders.cached.Loader', (settings.TEMPLATE_LOADERS)),)
        loader.template_source_loaders = None

    def remove_cache_template(self):
        from django.template import loader
        settings.TEMPLATE_LOADERS = settings.TEMPLATE_LOADERS[0][1]
        loader.template_source_loaders = None

    def modify_template_and_check(self, client, url, has_error,
                                  template_name='admin/change_form.html',
                                  text='Overwriting'):
        if not INSTALLED_DB_TEMPLATES:
            return
        from dbtemplates.models import Template
        text_change = '%s2' % text
        template = Template.objects.get(name=template_name)
        template.content = template.content.replace(text, text_change)
        template.save()
        if has_error:
            try:
                self.check_url(client, url)
                self.assertEqual(False, True)
            except:
                template.content = template.content.replace(text_change, text)
                template.save()
        else:
            try:
                self.check_url(client, url)
                template.content = template.content.replace(text_change, text)
                template.save()
            except:
                self.assertEqual(False, True)

    def test_smart_extends_add_form(self):
        client = self.__client_login()
        self.check_url(client, reverse('admin:auth_group_add'))

    def test_smart_extends_change_form(self):
        client = self.__client_login()
        user_pk = client.session.get('_auth_user_id')
        self.check_url(client, reverse('admin:auth_user_change', args=(user_pk,)))

    def test_smart_extends_cached_template_loaders(self):
        client = self.__client_login()
        user_pk = client.session.get('_auth_user_id')
        url = reverse('admin:auth_user_change', args=(user_pk,))
        self.check_url(client, url)
        self.modify_template_and_check(client, url, has_error=True)
        self.add_cache_template()
        self.check_url(client, url)
        self.modify_template_and_check(client, url, has_error=False)
        user_pk = client.session.get('_auth_user_id')
        self.check_url(client, reverse('admin:auth_user_change', args=(user_pk,)))
        self.remove_cache_template()
        self.modify_template_and_check(client, url, has_error=True)

    def test_smart_extends_over_write_option(self):
        client = self.__client_login()
        user_pk = client.session.get('_auth_user_id')
        url = reverse('admin:auth_user_change', args=(user_pk,))
        if INSTALLED_DB_TEMPLATES:
            from dbtemplates.models import Template
            template = Template.objects.get(name='admin/change_form.html')
            template.content = template.content.replace('smart_extends', 'extends')
            template.save()
        register.tag('extends', do_smart_extends)
        self.check_url(client, url)
        register.tag('extends', do_extends)
        if INSTALLED_DB_TEMPLATES:
            template.content = template.content.replace('smart_extends', 'extends')
            template.save()

    def test_smart_extends_check_old_template_loaders(self):
        from django.template import loader
        template_loaders = settings.TEMPLATE_LOADERS
        if INSTALLED_DB_TEMPLATES:
            settings.TEMPLATE_LOADERS = (settings.TEMPLATE_LOADERS[0],
                                         'example.app.filesystem.load_template_source') + settings.TEMPLATE_LOADERS[2:]
        else:
            settings.TEMPLATE_LOADERS = ('example.app.filesystem.load_template_source',) + settings.TEMPLATE_LOADERS[1:]
        loader.template_source_loaders = None
        self.test_smart_extends_cached_template_loaders()
        settings.TEMPLATE_LOADERS = template_loaders

    def test_smart_extends_errors(self):
        if not INSTALLED_DB_TEMPLATES:
            return
        client = self.__client_login()
        user_pk = client.session.get('_auth_user_id')
        url = reverse('admin:auth_user_change', args=(user_pk,))
        from dbtemplates.models import Template
        template = Template.objects.get(name='admin/change_form.html')
        # First error
        template.content = template.content.replace('{% smart_extends "admin/change_form.html" %}',
                                                    '{% smart_extends "admin/change_form.html" "hello" %}')
        template.save()
        self.check_error(client, url, TemplateSyntaxError)
        template.content = template.content.replace('{% smart_extends "admin/change_form.html" "hello" %}',
                                                    '{% smart_extends "admin/change_form.html" %}')
        template.save()
        # Second error
        template.content = template.content.replace('{% smart_extends "admin/change_form.html" %}',
                                                    '{% smart_extends "admin/change_form.html" %}{% smart_extends "admin/change_form.html" %}')
        template.save()
        self.check_error(client, url, TemplateSyntaxError)
        template.content = template.content.replace('{% smart_extends "admin/change_form.html" %}{% smart_extends "admin/change_form.html" %}',
                                                    '{% smart_extends "admin/change_form.html" %}')
        template.save()

        # Third error
        template.content = template.content.replace('{% smart_extends "admin/change_form.html" %}',
                                                    '{% smart_extends "admin/change_form2.html" %}')
        template.save()
        self.check_error(client, url, TemplateDoesNotExist)
        template.content = template.content.replace('{% smart_extends "admin/change_form2.html" %}',
                                                    '{% smart_extends "admin/change_form.html" %}')
        template.save()
