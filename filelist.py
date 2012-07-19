'''
Created on 2012-7-16

@author: Asvel
'''
testdir = "D:\\"
testdirlong = r"\\?\D:\temp\longpath\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890"
testfile = r"D:\temp\humansize.py"
testfilelong = r"\\?\D:\temp\longpath\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\1234567890123456789012345678901234567890\file.txt"

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
    import os
    
    result = Directory(os.path.basename(path))
    try:
        item_name = sorted(os.listdir(path))
        for x in item_name:
            newpath = os.path.join(path, x)
            if os.path.isdir(newpath):
                result.add_item(read_dir(newpath))
            else:
                #info = os.stat(newpath)
                #result.add_item(File(x, info.st_size, info.st_mtime))
                result.add_item(File(x))
    except:
        pass
    return result
    pass

def read_xml(path):
    pass

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

from timeit import Timer

import os

import ctypes
import ctypes.wintypes
cCreateFile = ctypes.windll.kernel32.CreateFileW
cGetFileSizeEx = ctypes.windll.kernel32.GetFileSizeEx
cCloseHandle = ctypes.windll.kernel32.CloseHandle
cGetFileAttributes = ctypes.windll.kernel32.GetFileAttributesW
def getsize(path):
    handle = cCreateFile(path, 0x120089, 7, 0, 3, 0, 0)
    size = ctypes.wintypes.LARGE_INTEGER(0)
    cGetFileSizeEx(handle, ctypes.byref(size))
    cCloseHandle(handle)
    return size.value
def getattr(path):
    return cGetFileAttributes(path)


def test():
    x = read_dir(testdir)
    #write_xml(x, "1.xml")
    #os.stat(testfilelong)
    #getsize(testfilelong)
    #getattr(testfilelong)
    #os.path.isdir(testfilelong)
    

print(Timer("test()", "from __main__ import test").timeit(1))
