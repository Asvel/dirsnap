# -*- coding: utf-8 -*-

import snapshot
import os

def dump_list_depth(obj, depth):
    depth += obj['from'].strip(os.sep).count(os.sep)
    list = snapshot.dump_list(obj)
    list = [x for x in list if x.strip(os.sep).count(os.sep) == depth]
    return list

def delete(obj, path):
    path_part = path[len(obj['from']) + 1:].split(os.sep)
    item = obj
    for part in path_part[:-1]:
        item = item['item'][part]
    del item['item'][path_part[-1]]

def test():
    with open("test.html", 'r', encoding='utf-8') as fp:
        dirobj = snapshot.load_html(fp.read())

    #delete(dirobj, r'M:\anime_chk\air')
    #output = snapshot.dump_html(dirobj)
    output = "\n".join(dump_list_depth(dirobj, 2))

    with open("test1.html", 'w', encoding='utf-8') as fp:
        fp.write(output)

if __name__ == '__main__':
    test()
