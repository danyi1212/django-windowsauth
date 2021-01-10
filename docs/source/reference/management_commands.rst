
Management Commands
===================

createwebconfig
---------------

Generate ``web.config`` files with configurations for your Django Project's IIS website

Arguments
    * **--name**, **-n** FastCGI Handler Name (default: Django FastCGI).
    * **--static**, **-s** Create a ``web.config`` to configure IIS to serve the static folder.
    * **--media**, **-m** Create a ``web.config`` to configure IIS to serve the media folder.
    * **--windowsauth**, **-w** Configure Windows Authentication as the only IIS Authentication option.
    * **--https** Configure HTTP to HTTPS Redirect using IIS's URL Rewrite module.
    * **--logs**, **-l** Path for the WFastCGI logs.
    * **--override**, **-f** Force override existing files.

.. note::
    Before using the **--static** or **--media** flags, make sure to configure correctly the ``STATIC_ROOT`` and ``MEDIA_ROOT`` settings.

.. warning::
    In order for the ``web.config`` files to work correctly, you will need to **unlock** some IIS Configuration Section.
    See the **Install and Setup IIS** section at :doc:`../installation/installation` docs.