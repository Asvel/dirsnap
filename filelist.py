import os
import sys
import time

os.stat_float_times(False)

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
            newitem = read_dir(newpath)
        subitem.append(newitem)
    result["sub"] = subitem
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

def main():
    if (len(sys.argv) == 2):
        if os.path.exists(sys.argv[1]):
            path = sys.argv[1]
            output_name = time.strftime("%Y%m%d_%H%M%S_")
            output_name += path.replace(":", "").replace("\\", "_").strip("_")
            path = "\\\\?\\" + path
            #print(path, output_name)
            if (os.path.isdir(path)):
                x = read_dir(path)
                #write_xml(x, output_name + ".xml")
                write_json(x, output_name + ".json")
                #write_json_compact(x, output_name + ".compact.json")
                #"""
        else:
            print("项目", sys.argv[1], "不存在")
    else:
        pass

if __name__ == "__main__":
    main()
    #from timeit import Timer
    #print(Timer("main()", "from __main__ import main").timeit(10))
