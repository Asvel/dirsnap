import os
import sys
import time

def make_longunc(path):
    '''生成长 UNC 路径
    
    path 要生成长 UNC 路径的路径
    返回 path 的长 UNC 形式
    如果 path 本来就是长 UNC 路径则原样返回
    '''
    if (os.path.__name__ == 'ntpath') and (not path.startswith('\\\\?\\')):
        path = '\\\\?\\' + path
    return path

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
    
    # 保存抓取时间
    now = int(time.time())
    
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

    os.stat_float_times(False)
    result = read_a_dir(path)
    os.stat_float_times(True)
    result['from'] = path.strip('\\?')
    result['time'] = now
    return result

def write_json(obj, file):
    '''输出 read_dir() 生成的对象 obj 为 JSON 文件 file
    
    obj 要输出的对象
    file 输出到的文件
    '''
    
    # 修改键名用于排序（子项目排在最后）
    def rename_key_for_sort(obj):
        for x in obj['item'].values():
            if 'item' in x:
                rename_key_for_sort(x)
        obj['|item'] = obj['item']
        del obj['item']
        return obj

    import json
    with open(file, 'w', encoding='utf-8') as fp:
        fp.write(json.dumps(
            obj = rename_key_for_sort(obj),
            ensure_ascii = False,
            check_circular = False,
            sort_keys = True,
            indent = '\t'
        ).replace('|', ''))

def read_json(file):
    '''读取 JSON 文件 file 到对象 obj
    
    file 要读取的文件
    返回读取到的对象
    '''
    import json
    with open(file, 'r', encoding='utf-8') as fp:
        return json.load(fp)

def write_tree(obj, file, indent = '\t'):
    '''输出对象 obj 为树形文件 file
    
    obj 要输出的对象，应由 read_dir() 生成
    file 输出到的文件
    indent 缩进
    '''
    def write_tree_dir(obj, depth):
        desc.append(indent * depth + obj['name'])
        for item in obj['zsub']:
            if 'zsub' not in item:
                desc.append(indent * (depth + 1) + item['name'])
            else:
                write_tree_dir(item, depth + 1)
    
    desc = []
    write_tree_dir(obj, 0)
    desc.append('')
    with open(file, 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(desc))

def write_list(obj, file):
    '''输出对象 obj 为列表文件 file
    
    obj 要输出的对象，应由 read_dir() 生成
    file 输出到的文件
    '''
    def write_list_dir(obj, path):
        path += '\\'
        desc.append(path)
        for item in obj['zsub']:
            if 'zsub' not in item:
                desc.append(path + item['name'])
            else:
                write_list_dir(item, path + item['name'])

    desc = []
    write_list_dir(obj, obj['name'][:-1])
    desc.append('')
    with open(file, 'w', encoding = 'utf-8') as fp:
        fp.write('\n'.join(desc))

def main():
    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) > 2:
        command = sys.argv[1]
        if command == 'get': #抓取
            #输出文件名格式
            datetime_format = '%Y%m%d_%H%M%S'
            filename_format = '{path}_{datetime}.json'
            filename_invalid = '\/:*?"<>|'
            filename_trans = str.maketrans({x: '_' for x in filename_invalid})
            
            #准备
            path = make_longunc(os.path.abspath(sys.argv[2] + '\\'))
            datetime = time.strftime(datetime_format)
            filename = filename_format.format(datetime = datetime, 
                path = path.strip(':\\?').translate(filename_trans))
            
            if os.path.isdir(path):
                #抓取
                dirtree = read_dir(path)
                
                #输出
                write_json(dirtree, filename)
                #write_tree(dirtree, filename.format(type = 't'))
                #write_list(dirtree, filename.format(type = 'l'))
            else:
                print('目录', path, '不存在')
        elif command == 're-json': #重构 JSON 文件
            path = make_longunc(os.path.abspath(sys.argv[2]))
            if os.path.isfile(path):
                dirtree = read_json(path)
                def sort_dir(obj):
                    obj['zsub'].sort(key = lambda x: x['name'].lower())
                    for x in obj['zsub']:
                        if 'zsub' in x:
                            sort_dir(x)
                sort_dir(dirtree)
                write_json(dirtree, path)
            else: 
                print('文件', path, '不存在')
    else:
        print('''
使用方法：
    filelist.py <命令> <参数>

命令：
    get 抓取文件列表并输出，参数为要抓取的目录
    re-json 重构(排序，缩进) JSON 文件

示例：
    filelist.py get C:\\''')

if __name__ == '__main__':
    main()
    #from timeit import Timer
    #print(Timer('main()', 'from __main__ import main').timeit(10))
