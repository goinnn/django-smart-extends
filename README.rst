.. contents::

=============
Smart extends
=============

.. image:: https://travis-ci.org/goinnn/django-smartextends
    :target: https://travis-ci.org/goinnn/django-smartextends

.. image:: https://badge.fury.io/py/django-smartextends.png
    :target: https://badge.fury.io/py/django-smartextends

.. image:: https://pypip.in/d/django-smartextends/badge.png
    :target: https://pypi.python.org/pypi/django-smartextends

Smart extends is a Django application that allows improve 

It is distributed under the terms of the license write in the same directory,
in the file COPYING.LGPLv3

Depencies
=========

Django 1.2 - 1.3 (Tested for those versions)

Django 1.1 - 1.1.X (There were two branches to those versions)

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

If you set TEMPLATE_DEBUG = True in settings.py you must patch django code. You can find the patch in the patches directoy. There are one patch for Django 1.1.X version, other for Django 1.2 and other for Django 1.3.

