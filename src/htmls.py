MAIN = """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    {body}
</body>
</html>
"""

CLI_HELP = """
目前支持的参数有 (<*> 代表您需填入的参数)
    --host=<host> 启动时监听的主机地址, 默认为 0.0.0.0
    --port=<port> 启动时的端口, 默认为 flask 默认值, 一般为 5000
    --watch-dir=<dir> / --watchdir=<dir> 启动时扫描的根文件夹, 将显示其内文件, 万物起源将从这里开始
    --debug (附加参数, 如果您携带此参数即视为启用, 下均同) 开启 flask 内置的 DEBUG 模式. 如果您不知道这是什么, 请勿附带.
    --no-recursion / --norecursion 是否不递归扫描(即扫描子文件夹), 默认值为 True, 携带本参数后禁用.
"""
