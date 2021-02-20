
Create Task Scheduler Jobs
==========================

It is usually necessary to **execute tasks** from you project on a schedule.
This module has a shortcut to create scheduled jobs for **Django management commands** in the **Windows Task Scheduler**.

.. warning::
    This feature requires the installation of the ``pywin32`` module.
    Install it with ``pip install pywin32``

Create a task
-------------

Creating a new task is done with the ``createtask`` command.

For example, lets say you want to run the following command every hour::

$ py manage.py say_hello --new-users

You can create a schedule with this command::

$ py manage.py createtask "say_hello --new-users" -i hours=1

Now the following command will be executed every hour by the Windows Task Scheduler.

Using predefined tasks
----------------------

Included with this module are some **predefined tasks** for some Django and Third-Party app management commands.
Those commands can be created using the ``--predefined`` or ``-p`` argument

:clearsessions:
    Clear expired sessions from database, once a week::

    $ py manage.py createtask clearsessions -p

.. seealso::
    See more at https://docs.djangoproject.com/en/3.1/ref/django-admin/#django-admin-clearsessions

:clean_duplicate_history:
    Clean duplicate history records from all models with history every 3 hours (from django-simple-history)::

    $ py manage.py createtask clean_duplicate_history -p

:clean_old_history:
    Clean history records older then 30 days from all models with history every day (from django-simple-history)::

    $ py manage.py createtask clean_old_history -p


.. seealso::
    See more at https://django-simple-history.readthedocs.io/en/latest/utils.html#utils

:process_tasks:
    Worker for background tasks processing (from django-background-tasks)::

    $ py manage.py createtask process_tasks -p


You can also create **multiple workers** by specifying different names with ``--name`` argument.

.. seealso::
    See more at https://django-background-tasks.readthedocs.io/en/latest/#running-tasks
