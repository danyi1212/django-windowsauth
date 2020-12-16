
Serve Static Files through IIS
==============================

Generally websites have static files such as CSS, JS, Images served to clients beside the primary responses.
Those files are considered as "Static Files" because they can be delivered without being generated, modified or processed.

In Django, static files can be served by the Django Framework itself. This is very convenient during **Development**, but is not suitable for **Production** use.

.. seealso:: About Serving Static Files: https://docs.djangoproject.com/en/3.1/howto/static-files/

For production use, it is advised to let the **Web Server** to serve the Static Files.
This is how it can be done:

.. note::
    This how-to describes serving both **Static Files** and **Media Files**.
    In case you don't need or use one of those features, you can just ignore the respective parts in the tutorial.

First you will need to configure the following settings:

.. code-block:: python

    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / "static"

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / "media"

The ``STATIC_URL`` represents the file path **over HTTP**, while the ``STATIC_ROOT`` directs to the **Physical path** of the files in the Web Server's OS.
Meanwhile from the **IIS** point of view, the **HTTPS path** is derived from the file's **Physical path** location.
Although this can be altered using **Virtual Directories**, it is usually advised not to.

The same applies for the ``MEDIA_URL`` and ``MEDIA_ROOT`` settings.

Next we will need to create ``web.config`` files in each folder to configure IIS to server Static Files.

.. note:: Any time the ``STATIC_ROOT`` setting is changes, you will need to start over from this step.

This can be done by running the ``createwebconfig`` management command:::

$ py manage.py createwebconfig -s -m

The ``-s`` switch is used configure the ``STATIC_ROOT`` folder, while ``-m`` switch is used to configure the ``MEDIA_ROOT`` folder.

Now all we need to do is to **collect** all the static files from the many Django apps into the ``STATIC_ROOT`` folder.
This can be done by running the ``collectstatic`` management command:::

$ py manage.py collectstatic

.. seealso:: About ``collectstatic`` command: https://docs.djangoproject.com/en/3.1/ref/contrib/staticfiles/#django-admin-collectstatic

At this point, in case you have configured the **URL path** and **Physical path** the same, the Web Server should serve all static files correctly.

In case you have configured **different paths**, you will probably want to setup **Virtual Directories**.

This can be useful when you want to store Static and / or Media file **outside** the Django project's folder (the website's root folder), on a separate disk for example.

To create the Virtual Directories:

#. Open **IIS Manager**
#. Right-click on **your website**
#. Click **"Add Virtual Directory..."**
#. Set the **"Alias"** for the same value as ``STATIC_URL`` setting
#. Set the **"Physical Path"** for the same value ``STATIC_ROOT`` setting

You may do the same with the ``MEDIA_URL`` and ``MEDIA_ROOT`` settings in order to add Virtual Directory for serving **Media Files**.

.. seealso:: Microsoft Docs on IIS Virtual Directories https://docs.microsoft.com/en-us/iis/get-started/planning-your-iis-architecture/understanding-sites-applications-and-virtual-directories-on-iis#virtual-directories