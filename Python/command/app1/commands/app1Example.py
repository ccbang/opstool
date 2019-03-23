from management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "简单演示app1."

    def add_arguments(self, parser):
        parser.add_argument('name', help='名称')

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        name = options["name"]
        try:
            self.stdout.write(self.style.ERROR(f"ERROR: app1 详细程度{verbosity}, stdout:{name}"))
            self.stdout.write(self.style.FUCK(f"FUCK: app1 详细程度{verbosity}, stdout:{name}"))
            if verbosity > 1:
                self.stdout.write(self.style.NOTICE(f"NOTICE: app1 详细程度{verbosity}, stdout:{name}"))
            if verbosity > 2:
                self.stdout.write(self.style.DEBUG(f"DEBUG: app1 详细程度{verbosity}, stdout:{name}"))
            self.stdout.write(self.style.WARNING(f"WARNING: app1 详细程度{verbosity}, stdout:{name}"))
            self.stdout.write(self.style.MANAGE(f"MANAGE: app1 详细程度{verbosity}, stdout:{name}"))
            self.stdout.write(self.style.SUCCESS(f"SUCCESS: app1 详细程度{verbosity}, stdout:{name}"))
        except ValueError:
            raise CommandError(f"app1 无法从你提供的{options['name']}中获取信息")
