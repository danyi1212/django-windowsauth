
Deployment Checklist
=====================

Before deploying your site to production it is important to go over some best practices and make sure your site is the **most stable and secure**.
Provided here are some best practices related to ``django-windowsauth``, IIS and LDAP.

Many checks can be performed automatically using ``py manage.py check --deploy``.

.. seealso::
    Check out `Django's deployment checklist <https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/>`_ too.

#. **Turn DEBUG off**. Make sure to never get it active on a production setup.
#. Store your **secrets** in a secure location. Here is a tutorial about :doc:`../howto/manage_secrets`.
#. Use a proper **cache backend**, and use ``WAUATH_USE_CACHE`` for better performance. More about `Django's cache framework <https://docs.djangoproject.com/en/3.1/topics/cache/>`_
#. Use a production ready **database backend**, not SQLite. `django-mssql-backend <https://github.com/ESSolutions/django-mssql-backend>`_ is a great backend for Microsoft SQL Server.
#. Configure ``ALLOWED_HOSTS`` and ``CSRF_TRUSTED_ORIGINS`` to exactly same as your **IIS Bindings**.
#. Setup Django **logging** and Admin Error Reporting for your project. See more https://docs.djangoproject.com/en/3.1/topics/logging/.
#. Enable and configure **IIS Logging**.
#. Keep your site files on a **separate drive** from the OS. Consider doing the same for logs and media.
#. Minimize to bare minimum permissions for the ``web.config`` files throughout your site.
#. Configure **HTTPS bindings** for your website with a CA signed certificate.
#. Use **only HTTPS** for your site, and configure HTTPS redirection with IIR Rewrite. Check out the ``--https`` flag for the ``createwebconfig`` command.
#. Use only **IIS Windows Authentication** when possible.
#. Protect your Django view using ``@login_required`` decorator and other authorization logics.
#. Use SSL and NTLM or Kerberos authentication for your LDAP connection. See :doc:`../howto/securing_ldap`.
#. Minimize the ``SESSION_COOKIE_AGE`` time and enable ``SESSION_EXPIRE_AT_BROWSER_CLOSE`` when using Windows Authentication as SSO. We recommend using 86400, 1 day in seconds.
#. :doc:`../howto/custom_error_pages` for a better user experience.
#. Configure recycling times for your Application Pool at the least used time of the day.
#. Consider increasing the Maximum Worker Processes in your Application Pool to accommodate for heavy loads.
#. Setup Request Filtering to your site to limit unintended file access. You should deny access to ".py" and ".config" file extensions.
#. Enable dynamic IP restrictions based of requests/ms.

.. seealso::
    Some more great best practices for IIS are available at https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/iis-best-practices/ba-p/1241577
