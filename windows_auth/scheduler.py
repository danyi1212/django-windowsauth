import os
from pathlib import Path
from typing import Optional

import win32com.client
from pythoncom import com_error

from django.conf import settings
from django.utils import timezone

_PROJECT_NAME = os.path.basename(settings.BASE_DIR)
_PYTHON_PATH = str(Path(os.environ.get("VIRTUAL_ENV")) / "Scripts" / "python.exe")

LOCAL_SYSTEM = "NT Authority\\LocalSystem"
LOCAL_SERVICE = "NT Authority\\LocalService"
NETWORK_SERVICE = "NT Authority\\NetworkService"
APPLICATION_POOL_IDENTITY = "IIS AppPool\\DefaultAppPool"


_scheduler = win32com.client.Dispatch('Schedule.Service')
_scheduler.Connect()


def _get_absolute_command_line(command_line):
    return f"{Path(settings.BASE_DIR) / 'manage.py'} {command_line}"


def create_task_definition(command_line, description: str = "", priority: int = 3,
                           timeout: timezone.timedelta = timezone.timedelta(hours=1)):
    """
    Create a new Scheduled Task definition for a Django Management Command.
    :param command_line: The management command with arguments.
    :param description: Task description.
    :param priority: Task priority https://docs.microsoft.com/en-us/windows/win32/taskschd/tasksettings-priority.
    :param timeout: Maximum execution time.
    :return: Task Definition https://docs.microsoft.com/en-us/windows/win32/taskschd/taskdefinition
    """
    # create task
    task_def = _scheduler.NewTask(0)
    task_def.RegistrationInfo.Description = description
    task_def.RegistrationInfo.Source = _PROJECT_NAME
    # run as a Service Account
    task_def.Principal.LogonType = 5
    task_def.Principal.RunLevel = 1
    # configure settings
    task_def.Settings.Enabled = True
    task_def.Settings.StopIfGoingOnBatteries = False
    task_def.Settings.StartWhenAvailable = True
    task_def.Settings.WakeToRun = True
    task_def.Settings.AllowDemandStart = True
    task_def.Settings.AllowHardTerminate = True
    task_def.Settings.Priority = priority
    task_def.Settings.ExecutionTimeLimit = f"PT{timeout.seconds}S"
    task_def.Settings.RestartCount = 3
    task_def.Settings.RestartInterval = "PT1M"

    # create action https://docs.microsoft.com/en-us/windows/win32/taskschd/actioncollection-create
    action = task_def.Actions.Create(0)
    # parameters https://docs.microsoft.com/en-us/windows/win32/taskschd/execaction
    action.Path = _PYTHON_PATH
    action.Arguments = _get_absolute_command_line(command_line)

    return task_def


def add_schedule_trigger(task_def, interval: timezone.timedelta,
                         random: Optional[timezone.timedelta] = None) -> None:
    """
    Add trigger for time scheduled executions.
    When interval is grater then one day, the interval is rounded to days.
    :param task_def: Task Definition https://docs.microsoft.com/en-us/windows/win32/taskschd/taskdefinition.
    :param interval: Time delta between executions.
    :param random: Randomize execution inside a time span.
    """
    trigger = task_def.Triggers.Create(2)  # daily trigger
    trigger.StartBoundary = timezone.now().isoformat()
    if interval.days:
        # if interval longer then a day
        trigger.DaysInterval = interval.days
    else:
        trigger.Repetition.Duration = "P1D"
        trigger.Repetition.Interval = f"PT{interval.seconds}S"

    if random:
        trigger.RandomDelay = f"PT{interval.seconds}S"


def register_task(task_def, name: str, folder: str = None,
                  username: str = LOCAL_SERVICE, password: Optional[str] = None) -> None:
    """
    Register new task definition to Windows Task Scheduler.
    :param task_def: Task Definition https://docs.microsoft.com/en-us/windows/win32/taskschd/taskdefinition.
    :param name: Task name.
    :param folder: Task folder (created automatically).
    :param username: Principal username (for service principals)
    :param password: Principal password
    """
    # set default folder
    if not folder:
        folder = _PROJECT_NAME

    # get or create folder
    root_folder = _scheduler.GetFolder("\\")
    try:
        task_folder = root_folder.GetFolder(folder)
    except com_error:
        task_folder = root_folder.CreateFolder(folder)

    # register task https://docs.microsoft.com/en-us/windows/win32/taskschd/taskfolder-registertaskdefinition
    task_folder.RegisterTaskDefinition(
        name,
        task_def,
        6,  # create or update
        username,
        password,
        1 if password else 3  # password or interactive token (user is logged on)
    )
