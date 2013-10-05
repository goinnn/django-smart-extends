.. contents::

====================
django-smart-extends
====================

.. image:: https://api.travis-ci.org/goinnn/django-smart-extends.png?branch=master
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

* `Django <https://www.djangoproject.com/>`_ >= 1.5 (master branch)
* There are specific branches for `Django 1.5.X and 1.4.X <https://github.com/goinnn/django-smart-extends/tree/django_1.4_and_1.5>`_, `1.3.X and 1.2.X <https://github.com/goinnn/django-smart-extends/tree/django_1.2_and_1.3>`_, and `1.1.X <https://github.com/goinnn/django-smart-extends/tree/django_1.1.X>`_ (Also there is an old and unmaintained branch of `Django 1.1.0 <https://github.com/goinnn/django-smart-extends/tree/django_1.1>`_ without the last changes)

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
==========

This application is useful when you want to overwrite a template of a application in your project.
Currently this in Django produce infinite recursion

This is an example with django.contrib.admin app, but django-smart-extends works with any application, **this is not only to the admin site**. This is very useful if you use reusable django apps or any CMS implemented in django.

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

Patche
======

If you set TEMPLATE_DEBUG = False in settings.py you must patch the django code. You can find the patch in the patches directoy::

    patch -p2 -N -d my/path/of/django/ < ./patches/patch.diff

Reported
========

 * `Ticket in Django trac <https://code.djangoproject.com/ticket/15053>`_
 * `Pull request to Django repository <https://github.com/django/django/pull/217>`_
