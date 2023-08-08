from version import VERSION
STR_VERSION = '.'.join([str(_) for _ in VERSION])
from app import scan_dirs, create_pages

import os
import sys
import asyncio
import argparse
from hypercorn.config import Config
from quart import Quart

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'这是一个仿照 python -m http.server 的文件下载服务器, 基于 python quart 版本号: {STR_VERSION}')
    parser.add_argument('--host', dest='host', default='0.0.0.0', help='启动时监听的主机地址, 默认为 0.0.0.0', type=str)
    parser.add_argument('--port', dest='port', default=None, help='启动时的端口, 默认为 quart 默认值, 一般为 5000', type=int)
    parser.add_argument('--watch-dir', '--watchdir', dest='watchdir', default=None, help='启动时扫描的根文件夹, 将显示其内文件, 万物起源将从这里开始', type=str)

    parser.add_argument('--debug', action='store_true', dest='debug', help='(附加参数, 如果您携带此参数即视为启用, 下均同) 开启 quart 内置的 DEBUG 模式. 如果您不知道这是什么, 请勿附带.')
    parser.add_argument('--no-recursion', action='store_false', dest='recursion', help='是否不递归扫描(即扫描子文件夹), 默认值为 False, 携带本参数后禁用.')
    parser.add_argument('--ignore-error', '--ignorerror', action='store_true', dest='ignore_error', help='忽略读取文件时发生的错误')
    args = parser.parse_args()

    HOST = args.host
    PORT = args.port
    WATCH_DIR = args.watchdir or os.getcwd()

    DEBUG = args.debug
    RECURSION = args.recursion
    IGNORE_ERROR = args.ignore_error

    if not DEBUG:
        if PORT is None:
            PORT = 5000

    if PORT is not None and not (1 <= PORT <= 65535):
        print(f'非法的端口号 {PORT}, 应 1 <= --port <= 65535')
        sys.exit(-1)

    RUNNING = os.environ.get('pyquart-file-server_running', '') == 'running'
    if not RUNNING:
        print(f'欢迎使用 pyquart-file-server V{STR_VERSION}, 由 爱喝牛奶 制作, 基于 MIT 协议开源\n当前监听路径: {WATCH_DIR}')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    from hypercorn.asyncio import serve
    app = Quart(__name__)

    create_pages(app, loop.run_until_complete(scan_dirs(root_path=WATCH_DIR, recursion=RECURSION, ignorerror=IGNORE_ERROR)))

    config = Config()
    config.bind = f"{HOST}:{PORT}"

    if DEBUG:
        if not RUNNING:
            print(f'开始使用开发环境运行')

        os.environ['pyquart-file-server_running'] = 'running'
        os.environ['QUART_ENV'] = 'development'  # 设置 quart 环境为开发
        config.loglevel = 'DEBUG'  # 日志等级
        config.accesslog = '-'  # 设置日志为默认输出, 没有本行直接 蹦蹦炸弹

        loop.run_until_complete(serve(app, config))
    else:
        if not RUNNING:
            print(f'开始使用生产环境运行: http://{HOST}:{PORT}\n提示: 如果您需要看查日志(包含访问信息和运行日志), 请重启此程序并附带 --debug 参数打开开发人员模式')

        config.loglevel = 'NOTSET'  # Make production environment to avoid logging stream output.

        loop.run_until_complete(serve(app, config))
