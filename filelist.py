import os
import sys
import time

os.stat_float_times(False)

class File:
    def __init__(self, name = "", size = 0, time = 0):
        self.name = name
        self.size = size
        self.time = time

class Directory:
    def __init__(self, name = "", item = None):
        self.name = name
        self.item = item
        if self.item is None:
            self.item = []
    def add_item(self, newitem):
        self.item.append(newitem)

def read_dir(path):
    result = Directory(os.path.basename(path))
    
    #读取子项目列表
    try:
        item_name = sorted(os.listdir(path))
    except:
        print("列出", path, "的子目录时发生异常")
        item_name = []
    
    #扩展子项目
    for x in item_name:
        newpath = os.path.join(path, x)
        if os.path.isdir(newpath):
            newitem = read_dir(newpath)
        else:
            try:
                info = os.stat(newpath)
                newitem = File(x, info.st_size, info.st_mtime)
            except:
                print("读取文件", newpath, "的信息时发生异常")
                newitem = File(x)
        result.add_item(newitem)
    return result

def json_output(obj, file):
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

def write_xml(dirobj, xmlfile):
    import xmlwitch
    xml = xmlwitch.Builder(version='1.0', encoding='utf-8', indent='\t')
    
    def write_xml_dir(dirobj):
        with xml.directory():
            xml.name(dirobj.name)
            if len(dirobj.item) > 0:
                with xml.item:
                    for x in dirobj.item:
                        if isinstance(x, Directory):
                            write_xml_dir(x)
                        else:
                            with xml.file:
                                xml.name(x.name)
                                xml.size(str(x.size))
                                xml.time(str(x.time))
                    
    write_xml_dir(dirobj)
    
    f = open(xmlfile, "wb")
    f.write(xml.get_document())
    f.close()

def write_json(dirobj, jsonfile):
    def json_serialize(dirobj):
        newitem = {}
        newitem["name"] = dirobj.name
        if len(dirobj.item) > 0:
            newlist = []
            newitem["sub"] = newlist
            for x in dirobj.item:
                if isinstance(x, Directory):
                    newlist.append(json_serialize(x))
                else:
                    newfile = {"name": x.name, "size": x.size, "time": x.time}
                    newlist.append(newfile)
        return newitem
    json_output(json_serialize(dirobj), jsonfile)

def write_json_compact(dirobj, jsonfile):
    def json_serialize_compact(dirobj):
        newdict = {}
        for x in dirobj.item:
            if isinstance(x, Directory):
                newitem = json_serialize_compact(x)
            else:
                newitem = {"size": x.size, "time": x.time}
            newdict[x.name] = newitem
        return newdict
    json_output(json_serialize_compact(dirobj), jsonfile)

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
            print(sys.argv[1], "do not exist")
    else:
        pass

if __name__ == "__main__":
    #main()
    from timeit import Timer
    print(Timer("main()", "from __main__ import main").timeit(10))
