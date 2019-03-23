### command 多app命令管理(argparse)

```参考Djagno manage```
#### 注意：每个app/commands下的文件名不能相同，有相同的只取第一个

![image](https://github.com/ccbang/opstool/blob/master/Python/command/show_command.PNG)

增加方法：只要app/commands增加对应文件
[python argparse doc](https://docs.python.org/zh-cn/3.7/library/argparse.html)
```python
from management.base import BaseCommand


class Command(BaseCommand):
    help = "帮助title."

    def add_arguments(self, parser):
        """这里是增加命令参数， 用法可以查看python doc
        parser.add_argument('name', help='名称')
        """
        pass

    def handle(self, *args, **options):
        """这里是你命令需要操作的内容，入口在这里"""
        pass
```