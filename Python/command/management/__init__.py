import functools
import os
import pkgutil
import sys
from collections import defaultdict
from difflib import get_close_matches
from importlib import import_module
from management.base import CommandError, CommandParser

from management.color import color_style
import settings


def find_commands(app_path) -> list:
    """
    根据提供的目录，返回存在的模块列表
    """
    command_dir = os.path.join(app_path, 'commands')
    return [
        name for _, name, is_pkg in pkgutil.iter_modules([command_dir])
        if not is_pkg and not name.startswith('_')
    ]


def load_command_class(app_name, name):
    """
    根据app_name和模块名称返回模块下Command方法实例
    如果发生错误，这里将会退出
    """
    module = import_module(f'{app_name}.commands.{name}')
    return module.Command()


@functools.lru_cache(maxsize=None)
def get_commands():
    commands = {name: 'management' for name in find_commands(__path__[0])}
    for app in settings.APPS:
        path = os.path.join(settings.BASE_DIR, app)
        commands.update({name: app for name in find_commands(path)})
    return commands


class ManagementUtility:
    """
    封装command.py 方法
    """

    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])

    def main_help_text(self, commands_only=False):
        """获取帮助文档."""
        if commands_only:
            usage = sorted(get_commands())
        else:
            usage = [
                "",
                "使用 '%s help <subcommand>' 查看更多的子命令帮助." % self.prog_name,
                "可使用的<subcommand>:",
            ]
            commands_dict = defaultdict(lambda: [])
            for name, app in get_commands().items():
                if app == 'management':
                    app = 'tools'
                else:
                    app = app.rpartition('.')[-1]
                commands_dict[app].append(name)
            style = color_style()
            for app in sorted(commands_dict):
                usage.append("")
                usage.append(style.NOTICE("[%s]" % app))
                for name in sorted(commands_dict[app]):
                    usage.append("    %s" % name)

        return '\n'.join(usage)

    def fetch_command(self, subcommand):
        """
        尝试获取 app_name 下commands目录的所有模块命令
        """
        # Get commands outside of try block to prevent swallowing exceptions
        commands = get_commands()
        try:
            app_name = commands[subcommand]
        except KeyError:
            possible_matches = get_close_matches(subcommand, commands)
            sys.stderr.write('Unknown command: %r' % subcommand)
            if possible_matches:
                sys.stderr.write('. Did you mean %s?' % possible_matches[0])
            sys.stderr.write("\nType '%s help' for usage.\n" % self.prog_name)
            sys.exit(1)
        klass = load_command_class(app_name, subcommand)
        return klass

    def execute(self):
        """
        根据参数，找出正在运行的子命令，创建对应实例，然后运行它
        """
        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = 'help'  # 如果没有给出参数，则显示帮助。

        parser = CommandParser(
            usage='%(prog)s subcommand [options] [args]',
            add_help=False,
            allow_abbrev=False
        )
        parser.add_argument('args', nargs='*')  # catch-all
        try:
            options, args = parser.parse_known_args(self.argv[2:])
        except CommandError:
            pass  # Ignore any option errors at this point.

        if subcommand == 'help':
            if '--commands' in args:
                sys.stdout.write(
                    self.main_help_text(commands_only=True) + '\n'
                )
            elif not options.args:
                sys.stdout.write(self.main_help_text() + '\n')
            else:
                self.fetch_command(
                    options.args[0]
                ).print_help(self.prog_name, options.args[0])

        elif subcommand == 'version' or self.argv[1:] == ['--version']:
            sys.stdout.write(settings.version + '\n')
        elif self.argv[1:] in (['--help'], ['-h']):
            sys.stdout.write(self.main_help_text() + '\n')
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)


def execute_from_command_line(argv=None):
    """Run a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()
