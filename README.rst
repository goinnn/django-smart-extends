.. contents::

====================
django-smart-extends
====================

.. image:: https://api.travis-ci.org/goinnn/django-smart-extends.png?branch=django_1.1.X
    :target: https://travis-ci.org/goinnn/django-smart-extends

.. image:: https://badge.fury.io/py/django-smart-extends.png
    :target: https://badge.fury.io/py/django-smart-extends

.. image:: https://pypip.in/d/django-smart-extends/badge.png
    :target: https://pypi.python.org/pypi/django-smart-extends

django-smart-extends is a Django application that allows improve the extension system of Django templates.

It is distributed under the terms of the license write in the same directory,
in the file COPYING.LGPLv3

Dependencies
============

* `Django <https://www.djangoproject.com/>`_ == 1.1

How to install
==============

In your settings.py
-------------------

::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.admin',

        ...

        'smartextends',

    )

And if you want:

::

    OVERWRITE_EXTENDS = True

How to use
----------

This application is useful when you want to overwrite a template of a application in your project.
Currently this in Django produce infinite recursion

If you set OVERWRITE_EXTENDS = True

file:admin/change_list.html

::

    {% extends "admin/change_list.html" %}

    {% block extrastyle %}
        {{ block.super }}
        <link rel="stylesheet" type="text/css" href="XXX" />
    {% endblock %}

Else:

file:admin/change_list.html

::

    {% smart_extends "admin/change_list.html" %}

    {% block extrastyle %}
        {{ block.super }}
        <link rel="stylesheet" type="text/css" href="XXX" />
    {% endblock %}

== Patches ==

If you set TEMPLATE_DEBUG = False in settings.py you must patch django code. You can find the patch in the patches directoy::

    patch -p1 -N -d my/path/of/django/template/ -i ./patches/patch.diff
