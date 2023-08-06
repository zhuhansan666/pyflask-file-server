from version import VERSION
STR_VERSION = '.'.join([str(_) for _ in VERSION])
from app import scan_dirs, create_pages

import os
import sys
import argparse
from flask import Flask

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'这是一个仿照 python -m http.server 的文件下载服务器, 基于 python flask 版本号: {STR_VERSION}')
    parser.add_argument('--host', dest='host', default='0.0.0.0', help='启动时监听的主机地址, 默认为 0.0.0.0', type=str)
    parser.add_argument('--port', dest='port', default=None, help='启动时的端口, 默认为 flask 默认值, 一般为 5000', type=int)
    parser.add_argument('--watch-dir', '--watchdir', dest='watchdir', default=None, help='启动时扫描的根文件夹, 将显示其内文件, 万物起源将从这里开始', type=str)

    parser.add_argument('--debug', action='store_const', dest='debug', default=False, help='(附加参数, 如果您携带此参数即视为启用, 下均同) 开启 flask 内置的 DEBUG 模式. 如果您不知道这是什么, 请勿附带.', const=True)
    parser.add_argument('--no-recursion', action='store_const', dest='no_recursion', default=False, help='是否不递归扫描(即扫描子文件夹), 默认值为 True, 携带本参数后禁用.', const=True)
    parser.add_argument('--ignore-error', '--ignorerror', action='store_const', dest='ignore_error', default=False, help='忽略读取文件时发生的错误', const=True)
    args = parser.parse_args()

    HOST = args.host
    PORT = args.port
    WATCH_DIR = args.watchdir or os.getcwd()

    DEBUG = args.debug
    RECURSION = not args.no_recursion
    IGNORE_ERROR = args.ignore_error

    if not DEBUG:
        if PORT is None:
            PORT = 5000

    if PORT is not None and not (0 <= PORT <= 65535):
        print('错误的端口号, 应 0 <= --port <= 65535')
        sys.exit(-1)

    RUNNING = os.environ.get('pyflask-file-server_running', '') == 'running'
    if not RUNNING:
        print(f'欢迎使用 pyflask-file-server V{STR_VERSION}, 由 爱喝牛奶 制作, 基于 MIT 协议开源\n当前监听路径: {WATCH_DIR}')

    app = Flask(__name__)
    create_pages(app, scan_dirs(WATCH_DIR, RECURSION, ignorerror=IGNORE_ERROR))

    if DEBUG:
        if not RUNNING:
            print(f'开始使用开发环境运行')
        os.environ['pyflask-file-server_running'] = 'running'
        os.environ['FLASK_ENV'] = 'development'  # 设置 flask 环境为开发
        app.run(host=HOST, port=PORT, debug=DEBUG)
    else:
        from waitress import serve
        if not RUNNING:
            print(f'开始使用生产环境运行: http://{HOST}:{PORT}\n提示: 如果您需要看查日志(包含访问信息和运行日志), 请附带 --debug 参数打开开发人员模式并重启此程序')
        serve(app, host=HOST, port=PORT)
