import os
import sys
import time

os.stat_float_times(False)

def read_dir(path):
    result = {"name": os.path.basename(path)}
    
    #读取子项目列表
    try:
        subitem_name = sorted(os.listdir(path))
    except:
        print("列出", path, "的子目录时发生异常")
        subitem_name = []
    
    #扩展子项目
    subitem = []
    for x in subitem_name:
        newpath = os.path.join(path, x)
        if not os.path.isdir(newpath):
            newitem = {"name": x}
            try:
                info = os.lstat(newpath)
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
