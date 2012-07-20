import os
import sys
import time

datetime_format = "%Y%m%d_%H%M%S"
filename_format = "fl{type}_{datetime}_{path}.txt"
#filename_json

filename_invalid = "\/:*?\"<>|"

os.stat_float_times(False)

def make_longunc(path):
    """生成长 UNC 路径
    
    path 要生成长 UNC 路径的路径
    返回 path 的长 UNC 形式
    如果 path 本来就是长 UNC 路径则原样返回
    """
    if not path.startswith("\\\\?\\"):
        path = "\\\\?\\" + path
    return path

def read_dir(path):
    """抓取目录列表为一个字典
    
    path 要抓取的目录
    
    返回值的结构：
    返回值由嵌套的字典和列表构成
    每个字典表示一个项目（文件或目录），每个列表包含一组字典
    每个字典有一个"name"键，值为该项目的名字
    如果该项目是一个目录，那么有一个"sub"键，值为该目录的子项目的列表
    如果该项目是一个文件，那么有"size"和"time"键，值分别为该文件的大小和修改时间
    """
    def read_dir_(path):
        result = {"name": os.path.basename(path)}
        
        #读取子项目列表
        try:
            subitem_name = sorted(os.listdir(path))
        except:
            print("列出目录", path, "的子项目时发生异常")
            subitem_name = []
        
        #扩展子项目
        subitem = []
        for x in subitem_name:
            newpath = os.path.join(path, x)
            if not os.path.isdir(newpath):
                newitem = {"name": x}
                try:
                    info = os.stat(newpath)
                    newitem["size"] = info.st_size
                    newitem["time"] = info.st_mtime
                except:
                    print("读取文件", newpath, "的信息时发生异常")
            else:
                newitem = read_dir_(newpath)
            subitem.append(newitem)
        result["sub"] = subitem
        return result
    
    result = read_dir_(path)
    result["name"] = path[4:]
    return result

def write_json(obj, file):
    """输出可序列化的对象 obj 为 JSON 文件 file
    
    obj 要输出的对象
    file 输出到的文件
    """
    import json
    fp = open(file, "w", encoding="utf-8")
    json.dump(
        obj = obj,
        fp = fp,
        ensure_ascii = False,
        check_circular = False,
        sort_keys = True,
        indent = "\t"
    )
    fp.close()

def read_json(file):
    """读取 JSON 文件 file 到对象 obj
    
    file 要读取的文件
    返回读取到的对象
    """
    import json
    with open(file, "w", encoding="utf-8") as fp:
        return json.load(fp)

def write_tree(obj, file, indent = "\t"):
    
    def write_tree_dir(obj, depth):
        desc.append(indent * depth + obj["name"])
        for item in obj["sub"]:
            if "sub" not in item:
                desc.append(indent * (depth + 1) + item["name"])
            else:
                write_tree_dir(item, depth + 1)
    
    desc = []
    write_tree_dir(obj, 0)
    desc.append("")
    with open(file, "w", encoding="utf-8") as fp:
        fp.write("\n".join(desc))

def main():
    datetime = time.strftime(datetime_format)
    if (len(sys.argv) > 2):
        command = sys.argv[1]
        if (command == "get"):
            path = make_longunc(sys.argv[2])
            filename = filename_format.format(type = "{type}", datetime = datetime, 
                path = path.translate(str.maketrans({k: "_" for k in filename_invalid})).strip("_"))
            if os.path.isdir(path):
                dirtree = read_dir(path)
                write_json(dirtree, filename.format(type = "j"))
                write_tree(dirtree, filename.format(type = "t"))
            else:
                print("目录", path, "不存在")
    else:
        print("""
使用方法：
    filelist.py <命令> <参数>

命令：
    get 抓取文件列表并输出，参数为要抓取的目录

示例：
    filelist.py get C:\\""")

if __name__ == "__main__":
    main()
    #from timeit import Timer
    #print(Timer("main()", "from __main__ import main").timeit(10))
