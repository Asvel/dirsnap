import os
import sys
import time
import json
import locale

def read_dir(path):
    '''抓取目录列表为一个字典
    
    path 要抓取的目录
    
    返回值的结构：
    {
        "from": <抓取的目录>
        "size": <抓取到的文件的总大小>
        "time": <抓取时间（秒）>
        "item": {
            <文件名>: {
                "size": <该文件的大小>
                "time": <该文件的修改时间>
            }
            <目录名>: {
                "size": <该目录的子项目的总大小>
                "time": <该目录的子项目的最后修改时间>
                "item"：{
                    <子项目，格式同上，递归结构>
                } 
            }
            ...
        }
    }
    '''
    
    # 读取一个目录
    def read_a_dir(path):
        
        # 获取子项目列表
        try:
            subitem_name = os.listdir(path)
        except:
            print('获取此目录的子项目时发生异常：', path[4:])
            return {'size': 0, 'time': -1, 'item': {}}
        
        # 获取子项目属性
        subitem = {}
        for x in subitem_name:
            newpath = os.path.join(path, x)
            if not os.path.isdir(newpath):
                try:
                    info = os.stat(newpath)
                    newitem = {'size': info.st_size, 'time': info.st_mtime}
                except:
                    print('获取此文件的属性时发生异常：', newpath[4:])
                    newitem = {'size': 0, 'time': -1}
            else:
                newitem = read_a_dir(newpath)
            subitem[x] = newitem
        
        # 计算此目录属性
        size = sum([x['size'] for x in subitem.values()] + [0])
        time = max([x['time'] for x in subitem.values()] + [0])
        return {'size': size, 'time': time, 'item': subitem}

    # 保存抓取时间
    now = float(time.time())
    
    # 抓取并添加信息
    result = read_a_dir(path)
    result['from'] = path.strip('\\?')
    result['time'] = now
    return result

def read_json(file):
    '''读取 JSON 文件 file 到对象 obj
    
    file 要读取的文件
    返回读取到的对象
    '''
    with open(file, 'r', encoding='utf-8') as fp:
        return json.load(fp)

def dump_json(obj):
    '''输出 read_dir() 生成的对象 obj 为 JSON 文件 file
    
    obj 要输出的对象
    file 输出到的文件
    '''
    
    def rename_key_for_sort(obj):
        '''修改键名用于排序（子项目排在最后）
        '''
        for x in obj['item'].values():
            if 'item' in x:
                rename_key_for_sort(x)
        obj['|item'] = obj['item']
        del obj['item']
        return obj

    return json.dumps(
        obj = rename_key_for_sort(obj),
        ensure_ascii = False,
        check_circular = False,
        sort_keys = True,
        indent = '\t'
    ).replace('|', '')

def _filename_sort_key(s):
    '''返回排序文件名的键值
    '''
    return locale.strxfrm(s.lower())

def dump_tree(obj, indent = '\t'):
    '''由对象 obj 生成树形表示的字符串
    
    obj 作为数据源的对象，应符合 read_dir() 的格式
    indent 缩进使用的字符串
    '''
    locale.setlocale(locale.LC_COLLATE, '')

    def dump_tree_dir(obj, depth):
        for name in sorted(obj['item'].keys(), key=_filename_sort_key):
            desc.append(indent * (depth + 1) + name)
            if 'item' in obj['item'][name]:
                dump_tree_dir(obj['item'][name], depth + 1)

    desc = [obj['from']]
    dump_tree_dir(obj, 0)
    return '\n'.join(desc)

def dump_list(obj):
    '''由对象 obj 生成列表表示的字符串
    
    obj 作为数据源的对象，应符合 read_dir() 的格式
    '''
    locale.setlocale(locale.LC_COLLATE, '')

    def dump_list_dir(obj, path):
        for name in sorted(obj['item'].keys(), key=_filename_sort_key):
            fullname = os.path.join(path, name)
            desc.append(fullname)
            if 'item' in obj['item'][name]:
                desc[-1] += os.sep
                dump_list_dir(obj['item'][name], fullname)

    desc = [obj['from'] + os.sep]
    dump_list_dir(obj, obj['from'] + os.sep)
    return '\n'.join(desc)

def main():
    
    # 命令行解析
    import argparse
    class ArgumentParser(argparse.ArgumentParser):
        def format_usage(self):
            return argparse.ArgumentParser.format_usage(self)\
                .replace('usage:', '用法：')
        def format_help(self):
            return argparse.ArgumentParser.format_help(self)\
                .replace('usage:', '用法：')\
                .replace('positional arguments:', '参数：')\
                .replace('\n\noptional arguments:', '')\
                .replace('show this help message and exit', '显示此帮助并退出')
    
    parser = ArgumentParser(
        description='抓取和转换目录快照',
        epilog='''\
备注：
  from 和 to 可以相同
  可以通过使用相同的来源和结果类型来重新整理文件文件

示例：
  %(prog)s C:
  %(prog)s C: result.json
  %(prog)s C: -tt list
  %(prog)s -ft json test.json -tt list list.txt
  %(prog)s -ft json test.json test.json
''',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('frompath', metavar='from', help='数据来源')
    parser.add_argument('topath', metavar='to', nargs='?', help='保存结果到')
    parser.add_argument('-ft', '--fromtype', default='dir',
        choices=['dir', 'json'],
        help='数据来源类型，默认为 %(default)s')
    parser.add_argument('-tt', '--totype', default='json',
        choices=['json', 'tree', 'list'],
        help='结果储存格式，默认为 %(default)s')
    args = parser.parse_args()

    def make_longunc(path):
        '''生成长 UNC 路径
        
        path 要生成长 UNC 路径的路径
        返回 path 的长 UNC 形式
        如果 path 本来就是长 UNC 路径则原样返回
        '''
        if (os.path.__name__ == 'ntpath') and not path.startswith('\\\\?\\'):
            path = '\\\\?\\' + path
        return path

    # 准备路径信息
    frompath = make_longunc(os.path.abspath(args.frompath + os.sep))
    if args.topath == None:
        if args.fromtype == 'dir':
            trans = str.maketrans({x: '_' for x in '\\/:*?"<>|'})
            topath = frompath.strip(':\\?').translate(trans)
            topath += time.strftime('_%Y%m%d_%H%M%S')
        else:
            topath = os.path.os.path.splitext(frompath)[0]
        typetrans = {'json':'.json', 'tree':'_tree.txt', 'list':'_list.txt'}
        topath += typetrans[args.totype]
    else:
        topath = args.topath
    topath = make_longunc(os.path.abspath(topath))
    
    # 操作！
    dirsnap =eval('read_{}(frompath)'.format(args.fromtype))
    with open(topath, 'w', encoding='utf-8') as fp:
        fp.write(eval('dump_{}(dirsnap)'.format(args.totype)))

if __name__ == '__main__':
    main()
    #from timeit import Timer
    #print(Timer('main()', 'from __main__ import main').timeit(10))
