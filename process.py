# -*- coding: utf-8 -*-

import snapshot
import re
import os

#def dump_list_depth()

def delete(obj, path):
    path_part = path[len(obj['from']) + 1:].split(os.sep)
    item = obj
    for part in path_part[:-1]:
        item = item['item'][part]
    del item['item'][path_part[-1]]

def main():
    filename = "test.html"
    with open(filename, 'r', encoding='utf-8') as fp:
        dirobj = snapshot.load_html(fp.read())
    exp = re.compile('^' + '[^\{0}]*?\{0}'.format(os.sep) * 4 + '$')
    dirlist = snapshot.dump_list(dirobj)
    dirlist = [x for x in dirlist if exp.match(x) is not None]
    split = re.compile('^.*\{0}(.*)\{0}$'.format(os.sep))
    dirlist = [split.match(x).group(1) for x in dirlist]
    print('\n'.join(dirlist))

def test():
    with open("test.html", 'r', encoding='utf-8') as fp:
        dirobj = snapshot.load_html(fp.read())

    delete(dirobj, r'M:\anime_chk\air')

    with open("test1.html", 'w', encoding='utf-8') as fp:
        fp.write(snapshot.dump_html(dirobj))

if __name__ == '__main__':
    #main()
    test()
