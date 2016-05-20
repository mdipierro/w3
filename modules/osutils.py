import collections
import os
import re

from gluon import URL


def get_files(path, ignore_dirs=['errors', 'sessions']):
    regex_folders = re.compile('^[\w].+[\w]$$')
    regex_files = re.compile('^[\w].+\.(py|html|css|js|jpe?g|png|gif|mpe?g4?)$')
    folder_maps = collections.defaultdict(list)
    folder_maps[path] = []
    for (root, dirnames, filenames) in os.walk(path, topdown=True):
        for dirname in dirnames:
            if regex_folders.match(dirname) and not dirname in ignore_dirs:
                children = []
                newpath = os.path.join(root, dirname)
                folder_maps[newpath] = children
                folder_maps[root].append({'name': dirname, 'children': children})
        for filename in filenames:
            if regex_files.match(filename):                
                link = URL(vars=dict(filename=os.path.join(root, filename)[len(path):]))
                folder_maps[root].append({'name': filename, 'link': link})
    files = folder_maps[path]
    return files
