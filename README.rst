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

Smart extends is a Django application that allows improve the extension system of Django

It is distributed under the terms of the license write in the same directory,
in the file COPYING.LGPLv3

Dependencies
============

* For trunk code you will need Django 1.4

* There are specific branches for Django 1.2.X, 1.3.X and 1.1.X (There were two branches to those versions)

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

 and if you want:

::

    OVERWRITE_EXTENDS = True

How to use
----------

This application is useful when you want to overwrite a template of a application in your project.
Currently this in Django produce infinite recursion

If you don't set OVERWRITE_EXTENDS = True

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

Patches
=======

If you set TEMPLATE_DEBUG = True in settings.py you must patch django code. You can find the patch in the patches directoy. There are one patch for Django 1.1.X version, other for Django 1.2 and other for Django 1.3. and Django 1.4

