
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

createtask
----------

Add a management command to Windows Task Scheduler.

Arguments
    * **command** Management command, wrapped with "command".
    * **--predefined**, **-p** Create from a predefined task.
    * **--name**, **-n** Task name.
    * **--desc**, **-d** Task description.
    * **--identity**, **-u** Task principal identity (default: "NT Authority\\LocalSystem").
    * **--folder**, **-f** Task folder location (default: Project's name).
    * **--interval**, **-i** Task execution interval as timedelta kwargs, e.g. "days=1,hours=12.5".
    * **--random**, **-r** Randomize execution time as timedelta kwargs, e.g. "days=1,hours=12.5".
    * **--timeout**, **-t** Execution time limit as timedelta kwargs, e.g. "days=1,hours=12.5" (default: 1 hour).
    * **--priority** Task priority https://docs.microsoft.com/en-us/windows/win32/taskschd/tasksettings-priority

Predefined tasks
    * **clearsessions** Clear sessions from database every week.
    * **clean_duplicate_history** Clean duplicate history records from all models with history every 3 hours (from django-simple-history).
    * **clean_old_history** Clean history records older then 30 days from all models with history every day (from django-simple-history).
    * **process_tasks** Worker for background tasks processing (from django-background-tasks).
