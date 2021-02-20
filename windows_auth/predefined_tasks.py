from django.utils import timezone

from windows_auth.scheduler import create_task_definition, add_schedule_trigger, register_task


def _get_options(options: dict, *args) -> dict:
    """
    Filter specific keys from a dictionary
    :param options: Source dictionary
    :param args: Keys to keep
    :return: Filtered dictionary
    """
    return {
        key: value
        for key, value in options.items()
        if key in args
    }


def clear_sessions_task(**options):
    """
    Clear sessions from database every week
    """
    task_def = create_task_definition("clearsessions",
                                      description=options.get("desc") or "Clear expired sessions from database",
                                      **_get_options(options, "priority", "timeout"))
    add_schedule_trigger(task_def, timezone.timedelta(weeks=1), random=timezone.timedelta(1))
    register_task(task_def, options.get("name") or "Clear Sessions",
                  **_get_options(options, "folder", "username", "password"))


def clean_duplicate_history_task(**options):
    """
    Clean duplicate history records from all models with history every 3 hours (from django-simple-history).
    """
    interval = options.get("interval") or timezone.timedelta(hours=3)
    task_def = create_task_definition(f"clean_duplicate_history -m {interval.seconds / 60} --auto",
                                      description=options.get(
                                          "desc") or "Clean duplicate history records from database",
                                      **_get_options(options, "priority", "timeout"))
    add_schedule_trigger(task_def, interval)
    register_task(task_def, options.get("name") or "Clean Duplicate History",
                  **_get_options(options, "folder", "username", "password"))


def clean_old_history_task(**options):
    """
    Clean history records older then 30 days from all models with history every day (from django-simple-history).
    """
    task_def = create_task_definition("clean_old_history --auto",
                                      description=options.get("desc") or "Clean old history records from database",
                                      **_get_options(options, "priority", "timeout"))
    add_schedule_trigger(task_def, timezone.timedelta(days=1))
    register_task(task_def, options.get("name") or "Clean Old History",
                  **_get_options(options, "folder", "username", "password"))


def process_tasks_task(**options):
    """
    Worker for background tasks processing (from django-background-tasks)
    """
    interval = options.get("interval") or timezone.timedelta(hours=1)
    task_def = create_task_definition(f"process_tasks --log-std --duration {interval.seconds}",
                                      description=options.get("desc") or "Background tasks worker",
                                      **_get_options(options, "priority", "timeout"))
    add_schedule_trigger(task_def, interval)
    task = register_task(task_def, options.get("name") or "Process background tasks",
                         **_get_options(options, "folder", "username", "password"))
    task.Run(None)  # start immediately
