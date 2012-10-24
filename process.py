# -*- coding: utf-8 -*-

import snapshot
import os

def select(obj, path):
    if not path.startswith(obj['from']):
        raise Exception("目标项目在快照范围之外")
    path_part = [x for x in path[len(obj['from']):].split(os.sep) if x != '']
    for part in path_part:
        obj = obj['item'][part]
    return obj

def dump_list_depth(obj, depth):
    depth += obj['from'].strip(os.sep).count(os.sep)
    list = snapshot.dump_list(obj)
    list = [x for x in list if x.strip(os.sep).count(os.sep) == depth]
    return list

def delete(obj, path):
    path, name = os.path.split(path.strip(os.sep))
    pathobj = select(obj, path)
    del pathobj['item'][name]

def rename(obj, src, newname):
    path, oldname = os.path.split(src.strip(os.sep))
    pathobj = select(obj, path)
    if newname not in pathobj:
        pathobj[newname] = pathobj[oldname]
    del pathobj[oldname]

def merge(obj1, obj2):
    items1 = obj1['item']
    items2 = obj2['item']
    newitems = {}
    for name in list(items1.keys()):
        if name in items2:
            newitems[name] = merge(items1[name], items2[name])
            del items2[name]
        else:
            newitems[name] = items1[name]
        del items1[name]
    for name in list(items2.keys()):
        newitems[name] = items2[name]
        del items2[name]
    return {'item':newitems}

def mkdir(obj, path):
    path, name = os.path.split(path.strip(os.sep))
    pathobj = select(obj, path)
    pathobj['item'][name] = {'item':{}}

def makedirs(obj, path):
    path_part = [x for x in path[len(obj['from']):].split(os.sep) if x != '']
    for part in path_part:
        if part not in obj['item']:
            obj['item'][part] = {'item':{}}
        obj = obj['item'][part]

def move(obj, src, dst):
    if dst.startswith(src):
        raise Exception("目标目录是源目录的子目录")

    srcpath, srcname = os.path.split(src.strip(os.sep))
    dstpath, dstname = os.path.split(dst.strip(os.sep))
    makedirs(obj, dstpath)
    srcpathitem = select(obj, srcpath)['item']
    dstpathitem = select(obj, dstpath)['item']

    if dstname in dstpathitem:
        dstpathitem[dstname] = merge(srcpathitem[srcname], dstpathitem[dstname])
    else:
        dstpathitem[dstname] = srcpathitem[srcname]
    del srcpathitem[srcname]

def test():
    with open("test.html", 'r', encoding='utf-8') as fp:
        dirobj = snapshot.load_html(fp.read())

    #delete(dirobj, r'M:\anime_chk\air')
    #output = "\n".join(dump_list_depth(dirobj, 2))
    move(dirobj, r'M:\anime_a', r'M:\anime')
    output = snapshot.dump_html(dirobj)

    with open("test1.html", 'w', encoding='utf-8') as fp:
        fp.write(output)

if __name__ == '__main__':
    test()
