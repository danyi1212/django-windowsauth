import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser, CommandError
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = "Generate a web.config files for IIS Configuration."

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--name", "-n", default="Django FastCGI", type=str, help="FastCGI Handler Name")
        parser.add_argument("--static", "-s", action="store_true", help="Configure IIS to serve static folder")
        parser.add_argument("--media", "-m", action="store_true", help="Configure IIS to serve media folder")
        parser.add_argument("--windowsauth", "-w", action="store_true", help="Configure IIS for Windows Authentication")
        parser.add_argument("--logs", "-l", default=settings.BASE_DIR / "logs", type=str, help="Logs folder path")
        parser.add_argument("--override", "-f", action="store_true", help="Force override existing files")

    def handle(self, name=None, static=False, media=False, windowsauth=False, logs=None, override=False, **options):
        mode = "w" if override else "x"
        virtual_dirs = []

        # add static virtual directory
        if static:
            virtual_dirs.append({
                "url": settings.STATIC_URL,
                "path": settings.STATIC_ROOT,
            })

        # add media virtual directory
        if media:
            virtual_dirs.append({
                "url": settings.MEDIA_URL,
                "path": settings.MEDIA_ROOT,
            })

        # create root website web.config
        try:
            with open("web.config", mode) as file:
                file.write(render_to_string(
                    "windows_auth/iis_configs/root.config",
                    {
                        "django_settings": os.environ["DJANGO_SETTINGS_MODULE"],
                        "base_dir": settings.BASE_DIR,
                        "venv_path": os.environ["VIRTUAL_ENV"],
                        "handler_name": name,
                        "wsgi": settings.WSGI_APPLICATION,
                        "logs_folder": logs,
                        "windows_auth": windowsauth,
                    })
                )
            print("Created web.config file")
        except FileExistsError:
            print("web.config already exist. Use --override / -f to force override of the existing web.config.")

        # create a web.config to allow serving static files for each virtual directory path
        for virtual_dir in virtual_dirs:
            # create folder if does not exist
            if not os.path.exists(virtual_dir["path"]):
                print(virtual_dir['url'] + " virtual directory source folder does not exist, creating...")
                os.makedirs(virtual_dir["path"])

            try:
                with open(Path(virtual_dir["path"]) / "web.config", mode) as file:
                    file.write(render_to_string(
                        "windows_auth/iis_configs/serve.config",
                        {"handler_name": name})
                    )
                print("Created web.config file for " + virtual_dir['url'] + " virtual directory")
            except FileExistsError:
                print(virtual_dir['url'] + " web.config already exist. Use --override / -f to force "
                                           "override of the existing web.config.")
