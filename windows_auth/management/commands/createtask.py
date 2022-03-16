import os
from argparse import ArgumentTypeError

from django.conf import settings
from django.core.management import BaseCommand, CommandParser, CommandError
from django.utils import timezone
from pythoncom import com_error

from windows_auth.scheduler import create_task_definition, LOCAL_SERVICE, add_schedule_trigger, register_task
from windows_auth.predefined_tasks import clear_sessions_task, clean_duplicate_history_task, clean_old_history_task, process_tasks_task


def parse_datetime(string):
    result = {}
    for arg in string.split(","):
        if arg:
            try:
                # split key & value
                key, value = arg.split("=", 2)
            except ValueError:
                raise ArgumentTypeError("Argument must be in \"key=value\" format.")

            try:
                # parse to float
                result[key] = float(value)
            except ValueError as e:
                raise ArgumentTypeError(e)
    try:
        # create time delta
        return timezone.timedelta(**result)
    except TypeError as e:
        raise ArgumentTypeError(str(e).replace("__new__()", "timedelta()"))


PREDEFINED_TASKS = {
    "clearsessions": clear_sessions_task,
    "clean_duplicate_history": clean_duplicate_history_task,
    "clean_old_history": clean_old_history_task,
    "process_tasks": process_tasks_task,
}


class Command(BaseCommand):
    help = "Add a management command to Windows Task Scheduler."

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("command", help="Management command, wrapped with \"command\"")
        parser.add_argument("-p", "--predefined", action="store_true",
                            help=f"Create from a predefined task {tuple(PREDEFINED_TASKS.keys())}")
        parser.add_argument("-n", "--name", type=str, help="Task name")
        parser.add_argument("-d", "--desc", type=str, default="", help="Task description")
        parser.add_argument("-u", "--identity", type=str, default=LOCAL_SERVICE, help="Task principle identity"),
        parser.add_argument("-f", "--folder", type=str, default=os.path.basename(settings.BASE_DIR),
                            help="Task folder location")
        parser.add_argument("-i", "--interval", type=parse_datetime,
                            help="Task interval as timedelta kwargs, e.g. \"days=1,hours=12.5\".")
        parser.add_argument("-r", "--random", type=parse_datetime,
                            help="Randomize execution time as timedelta kwargs, e.g. \"days=1,hours=12.5\".")
        parser.add_argument("-t", "--timeout", type=parse_datetime, default="hours=1",
                            help="Execution Time Limit as timedelta kwargs, e.g. \"days=1,hours=12.5\".")
        parser.add_argument("--priority", type=int, default=3,
                            help="Task Priority "
                                 "https://docs.microsoft.com/en-us/windows/win32/taskschd/tasksettings-priority")

    def handle(self, command="", predefined=False, name=None, desc="", identity=LOCAL_SERVICE, folder=None,
               interval=None, random=None, timeout=None, priority=None, **options):
        try:
            if predefined:
                if command not in PREDEFINED_TASKS:
                    raise CommandError(f"Predefined task for \"{command}\" does not exist.")
                create_task = PREDEFINED_TASKS[command]
                create_task(command=command, name=name, desc=desc, identity=identity, folder=folder,
                            interval=interval, random=random, timeout=timeout, priority=priority)
            else:
                # create task definition
                task_def = create_task_definition(command, description=desc, priority=priority, timeout=timeout)
                # add trigger
                if interval:
                    add_schedule_trigger(task_def, interval, random=random)
                # register task
                register_task(task_def, name or command.split(" ", 1)[0], folder=folder, username=identity)
        except com_error as e:
            raise CommandError("Failed to register task. Did you run as administrator?\n" + str(e))
