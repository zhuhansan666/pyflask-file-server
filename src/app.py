from htmls import MAIN

import asyncio
import pathlib
from typing import Callable
from quart import Quart, send_file
from typing import Union
import os

FMapping = dict[Union["files", "dirs"], list[pathlib.Path]]

def catch(func: Callable):
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("What the hell?")
            if not kwargs.get('ignorerror', True):
                raise
    return _wrapper


def async_catch(func: Callable):
    async def _async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print("What the hell?")
            if not kwargs.get('ignorerror', True):
                raise
    return _async_wrapper

async def scan_dirs(root_path: str | pathlib.Path, recursion: bool=True, callback: Callable=None, ignorerror: bool=True):
    root_path = pathlib.Path(root_path) if type(root_path) == str else root_path
    # on Windows, like {"C:\": { "files": ["C:\foo_file", "C:\bar"], "dirs": ["C:\foo"] }}
    # on Linux and Mac OS, like {"/": { "files:" ["/foo", "/bar"], "dirs": [

    files = { str(root_path): { 'files': set(), 'dirs': set() } }

    @async_catch
    async def scan_children_dirs(path: pathlib.Path, ignorerror: bool=ignorerror):
        cc_tasks = set()

        if files.get(str(path), None) is None:
            files[str(path)] = {'dirs': set(), 'files': set()}

        for f in path.iterdir():
            if f.is_dir():
                files[str(path)]['dirs'].add(str(f))
                cc_tasks.add(scan_children_dirs(f))
                continue

            files[str(path)]['files'].add(str(f))

        await asyncio.gather(*cc_tasks)

    sc_tasks = set()
    for f in root_path.iterdir():
        if f.is_dir():
            # { '/' : { 'dirs': ['/etc'], '/etc': { 'dirs': [] } }
            files[str(root_path)]['dirs'].add(str(f))
            sc_tasks.add(scan_children_dirs(f)) if recursion else None
            continue

        files[str(root_path)]['files'].add(str(f))


    await asyncio.gather(*sc_tasks)

    return root_path, files

def create_pages(app: Quart, scan_dirs_tuple: FMapping):
    root_path = scan_dirs_tuple[0]
    scan_dirs_data = scan_dirs_tuple[1]
    for path, _dict in scan_dirs_data.items():
        files = sorted(_dict['files'])
        dirs = sorted(_dict['dirs'])

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
                async def _():
                    return await send_file(filename, as_attachment=True)
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
            async def _():
                return html
            return _

        app.add_url_rule(urlpath, urlpath, func(html), methods=['GET'])


if __name__ == '__main__':
    # this is some tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Quart(__name__)
    create_pages(app, loop.run_until_complete(scan_dirs('D:\\', ignorerror=True)))
    app.run('0.0.0.0', debug=True)
