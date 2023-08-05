from htmls import MAIN

from typing import Callable
from flask import Flask, send_file
import os

def scan_dirs(root_path: str, recursion: bool=True, callback: Callable=None, ignorerror: bool=False):
    root_path = os.path.normpath(root_path)
    files = { root_path: { 'files': [], 'dirs': [] } }  # files list
    # on Windows, like {"C:\": { "files": ["C:\foo_file", "C:\bar"], "dirs": ["C:\foo"] }}
    # on Linux and Mac OS, like {"/": { "files:" ["/foo", "/bar"], "dirs": ["/etc"] }}
    try:
        for file in os.listdir(root_path):
            full_filename = os.path.normpath(os.path.join(root_path, file))
            if os.path.isfile(full_filename):  # file
                if callback is not None:
                    try:
                        if not callback(full_filename):
                            continue
                    except Exception as e:
                        pass

                files[root_path]['files'].append(full_filename)
            else:  # dir
                if recursion:
                    try:
                        files_dict = scan_dirs(full_filename, recursion, callback)[1]
                        files[root_path]['dirs'].append(full_filename)  # 在 scan_dirs 后添加以免其报错了还是没有删掉
                        for path, file_list in files_dict.items():
                            files[path] = file_list
                    except Exception as e:
                        if not ignorerror:
                            raise e

    except Exception as e:
        if not ignorerror:
            raise e

    return root_path, files

def create_pages(app: Flask, scan_dirs_tuple: dict[list]):
    root_path = scan_dirs_tuple[0]
    scan_dirs_data = scan_dirs_tuple[1]

    for path, _dict in scan_dirs_data.items():
        files = _dict['files']
        dirs = _dict['dirs']

        path = os.path.relpath(path, root_path)
        urlpath = '/' + (path if path != '.' and path != root_path else '') + '/'
        urlpath = urlpath.replace('\\', '/')
        urlpath = '/' if urlpath == '//' else urlpath

        body = f'<h1>Directory listing for {urlpath}</h1><hr>'
        body += f'\t<div class="built-in_dir-link" href="./">./</div>\n'
        body += f'\t<a class="built-in_dir-link" href="../">../</a>\n<br>\n'        

        for file in files:
            url_filename = '/' + os.path.relpath(file, root_path).replace('\\', '/')

            def func(filename):
                def _():
                    return send_file(filename, as_attachment=True)
                return _

            app.add_url_rule(url_filename, url_filename, func(os.path.abspath(file)), methods=['GET'])
            file = os.path.split(file)[1]
            body += f'\t<a class="file-link" href="{url_filename}">{file}</a>\n<br>\n'

        for dir in dirs:
            url_dirname = '/' + os.path.relpath(dir, root_path).replace('\\', '/') + '/'

            dir = os.path.split(dir)[1].replace("\\", "/") + "/"
            body += f'\t<a class="dir-link" href="{url_dirname}">{dir}</a>\n<br>\n'
        body += '<hr>'

        html = MAIN.format(title=f'Directory listing for {urlpath}', body=body)

        def func(html):
            def _():
                return html
            return _

        app.add_url_rule(urlpath, urlpath, func(html), methods=['GET'])


if __name__ == '__main__':
    app = Flask(__name__)
    create_pages(app, scan_dirs('D:\\Admin\\Downloads'))
    app.run('0.0.0.0', debug=True)
