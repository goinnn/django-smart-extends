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

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


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
        settings.DEBUG = False
        settings.TEMPLATE_DEBUG = False
        response = client.get(url)
        str_extension = 'Overwriting the change_form template in our project without to have to copy every line of this template in our project'
        self.assertEqual(str_extension in response.content.decode('utf-8'), True)

    def test_smart_extends_add_form(self):
        client = self.__client_login()
        self.check_url(client, reverse('admin:auth_group_add'))

    def test_smart_extends_change_form(self):
        client = self.__client_login()
        user_pk = client.session.get('_auth_user_id')
        self.check_url(client, reverse('admin:auth_user_change', args=(user_pk,)))
