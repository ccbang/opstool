import os
import sys
from argparse import ArgumentParser, HelpFormatter
from io import TextIOBase

import settings
from management.color import color_style, no_style


class CommandError(Exception):
    """
     如果在执行管理期间引发此异常命令，它将被捕获并变成一个很好的打印错误
     消息到适当的输出流（即stderr）; 作为一个结果，提出这个例外（有一个明智的描述错误）
     是表明事情已经消失的首选方式执行命令时出错
    """
    pass


class CommandParser(ArgumentParser):
    """
    Customized ArgumentParser class to improve some error messages and prevent
    SystemExit in several occasions, as SystemExit is unacceptable when a
    command is called programmatically.
    """

    def __init__(self, **kwargs):
        self.missing_args_message = kwargs.pop('missing_args_message', None)
        self.called_from_command_line = kwargs.pop(
            'called_from_command_line', None
        )
        super().__init__(**kwargs)

    def parse_args(self, args=None, namespace=None):
        # Catch missing argument for a better error message
        if (
            self.missing_args_message and
            not (args or any(not arg.startswith('-') for arg in args))
        ):
            self.error(self.missing_args_message)
        return super().parse_args(args, namespace)

    def error(self, message):
        if self.called_from_command_line:
            super().error(message)
        else:
            raise CommandError("Error: %s" % message)


class DjangoHelpFormatter(HelpFormatter):
    """
    Customized formatter so that command-specific arguments appear in the
    --help output before arguments common to all commands.
    """
    show_last = {
        '--version',
        '--verbosity',
        '--no-color',
    }

    def _reordered_actions(self, actions):
        return sorted(
            actions,
            key=lambda a: set(a.option_strings) & self.show_last != set()
        )

    def add_usage(self, usage, actions, *args, **kwargs):
        super().add_usage(
            usage, self._reordered_actions(actions), *args, **kwargs
        )

    def add_arguments(self, actions):
        super().add_arguments(self._reordered_actions(actions))


class OutputWrapper(TextIOBase):
    """
    Wrapper around stdout/stderr
    """

    @property
    def style_func(self):
        return self._style_func

    @style_func.setter
    def style_func(self, style_func):
        if style_func and self.isatty():
            self._style_func = style_func
        else:
            self._style_func = lambda x: x

    def __init__(self, out, style_func=None, ending='\n'):
        self._out = out
        self.style_func = None
        self.ending = ending

    def __getattr__(self, name):
        return getattr(self._out, name)

    def isatty(self):
        return hasattr(self._out, 'isatty') and self._out.isatty()

    def write(self, msg, style_func=None, ending=None):
        ending = self.ending if ending is None else ending
        if ending and not msg.endswith(ending):
            msg += ending
        style_func = style_func or self.style_func
        self._out.write(style_func(msg))


class BaseCommand:
    """
    1. ``command.py`` 调用 ``run_from_argv()`` .

    2. ``run_from_argv()`` 调用 ``create_parser()`` 获得 ``ArgumentParser``对象,
       然后调用execute()来解析参数

    3. ``execute()`` 获得参数后传递给 ``handle()`` 处理;
       所有的输出将从handle()产生.

    4. 如果 ``handle()`` or ``execute()`` 返回错误 (e.g.
       ``CommandError``), ``run_from_argv()`` 会输出到 系统标准错误中.

    ``help``
        该子命令的一个帮助文档

    ``stealth_options``
        tuple 不参与参数解析
    """
    help = ''

    _called_from_command_line = False
    base_stealth_options = ('skip_checks', 'stderr', 'stdout')
    # 特定于命令的选项未由参数解析器定义
    stealth_options = ()

    def __init__(self, stdout=None, stderr=None, no_color=False):
        self.stdout = OutputWrapper(stdout or sys.stdout)
        self.stderr = OutputWrapper(stderr or sys.stderr)
        if no_color:
            self.style = no_style()
        else:
            self.style = color_style()
            self.stderr.style_func = self.style.ERROR

    def get_version(self):
        return settings.version

    def create_parser(self, prog_name, subcommand):
        """
        创建并返回ArgumentParser, 这将用于解析此命令的参数。
        """
        parser = CommandParser(
            prog='%s %s' % (os.path.basename(prog_name), subcommand),
            description=self.help or None,
            formatter_class=DjangoHelpFormatter,
            missing_args_message=getattr(self, 'missing_args_message', None),
            called_from_command_line=getattr(
                self, '_called_from_command_line', None
            ),
        )
        parser.add_argument(
            '--version', action='version', version=self.get_version()
        )
        parser.add_argument(
            '-v',
            '--verbosity',
            action='store',
            dest='verbosity',
            default=1,
            type=int,
            choices=[0, 1, 2, 3],
            help='詳細程度; 0=最小輸出, 1=正常輸出, 2=詳細輸出, 3=非常詳細輸出'
        )
        parser.add_argument(
            '--no-color',
            action='store_true',
            dest='no_color',
            help="不要着色命令输出.",
        )
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        """
        用于添加自定义参数的子类命令的入口
        """
        pass

    def print_help(self, prog_name, subcommand):
        """
        打印帮助文档， 来源于``self.usage()``.
        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv):
        """
        处理提供的参数，并尝试运行
        """
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], argv[1])

        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop('args', ())
        try:
            self.execute(*args, **cmd_options)
        except Exception as e:
            if not isinstance(e, CommandError):
                raise

            self.stderr.write('%s: %s' % (e.__class__.__name__, e))
            sys.exit(1)

    def execute(self, *args, **options):
        """
        尝试执行命令，并根据参数输出
        """
        if options['no_color']:
            self.style = no_style()
            self.stderr.style_func = None
        if options.get('stdout'):
            self.stdout = OutputWrapper(options['stdout'])
        if options.get('stderr'):
            self.stderr = OutputWrapper(
                options['stderr'], self.stderr.style_func
            )

        output = self.handle(*args, **options)
        if output:
            self.stdout.write(output)
        return output

    def handle(self, *args, **options):
        """
        继承类必须定义handle()方法，用来执行该命令
        """
        raise NotImplementedError(
            'subclasses of BaseCommand must provide a handle() method'
        )
