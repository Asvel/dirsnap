# -*- coding: utf-8 -*-

import snapshot
import re
import os

def main():
    filename = r"C:\project\OfflineDirectory\test.html";
    with open(filename, 'r', encoding='utf-8') as fp:
        dirobj = snapshot.load_html(fp.read())
    exp = re.compile('^' + '[^\{0}]*?\{0}'.format(os.sep) * 4 + '$')
    dirlist = snapshot.dump_list(dirobj)
    dirlist = [x for x in dirlist if exp.match(x) is not None]
    split = re.compile('^.*\{0}(.*)\{0}$'.format(os.sep))
    dirlist = [split.match(x).group(1) for x in dirlist]
    print('\n'.join(dirlist))

if __name__ == '__main__':
    main()
