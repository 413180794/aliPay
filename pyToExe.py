#!/usr/bin/env python3
# -\- coding: utf-8 -\-
import shutil

from PyInstaller.__main__ import run
# -F:打包成一个EXE文件 
# -w:不带console输出控制台，window窗体格式 
# --paths：依赖包路径 
# --icon：图标 
# --noupx：不用upx压缩 
# --clean：清理掉临时文件

from profile import profile

if __name__ == '__main__':
    opts = ['-F',"-w" ,r'--paths=' + profile.QT_BIN_URL,
            r'--paths=' + profile.QT_PLUGINS_URL,
            '--noupx', '--clean',
            'manage.py']
    # opts = ['-F',
    #         '--noupx', '--clean',
    #         'manage.py']

    run(opts)
    shutil.copy(profile.EXE_URL, profile.NEW_EXE_URL)
