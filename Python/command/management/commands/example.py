#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-01-11 11:41:02
# @Author  : ccbang (libanglong@hotmail.com)
# @Link    : https://github.com/ccbang
# @Version : $Id$
from management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "简单演示."

    def add_arguments(self, parser):
        parser.add_argument('name', help='名称')

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        name = options["name"]
        try:
            self.stdout.write(self.style.ERROR(f"ERROR: 详细程度{verbosity}, stdout:{name}"))
            self.stdout.write(self.style.FUCK(f"FUCK: 详细程度{verbosity}, stdout:{name}"))
            if verbosity > 1:
                self.stdout.write(self.style.NOTICE(f"NOTICE: 详细程度{verbosity}, stdout:{name}"))
            if verbosity > 2:
                self.stdout.write(self.style.DEBUG(f"DEBUG: 详细程度{verbosity}, stdout:{name}"))
            self.stdout.write(self.style.WARNING(f"WARNING: 详细程度{verbosity}, stdout:{name}"))
            self.stdout.write(self.style.MANAGE(f"MANAGE: 详细程度{verbosity}, stdout:{name}"))
            self.stdout.write(self.style.SUCCESS(f"SUCCESS: 详细程度{verbosity}, stdout:{name}"))
        except ValueError:
            raise CommandError(f"无法从你提供的{options['name']}中获取信息")
