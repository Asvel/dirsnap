'''
Created on 2012-7-16

@author: Asvel
'''
testdir = r"D:\temp"
testfile = r"D:\temp\humansize.py"

import os

class item:
    def __init__(self, path = ""):
        (self.path, self.name) = ("", "")
        self.setpath(path)
    def setpath(self, path):
        (self.path, self.name) = os.path.split(path)
        
class file(item):
    def __init__(self, path = ""):
        item.__init__(self, path)
        self.size = 0
        self.time = 0
        self.setpath(path)
    def setpath(self, path):
        item.setpath(self, path)
        if (path != ""):
            info = os.stat(path)
            self.size = info.st_size
            self.time = info.st_mtime

class directory(item):
    def __init__(self, path = ""):
        item.__init__(self, path)
        self.item = []
        if (path != ""):
            for t in os.listdir(path):
                newpath = os.path.join(path, t)
                newitem = (os.path.isdir(newpath) and directory or file)(newpath)
                self.item.append(newitem)
    def setpath(self, path):
        item.setpath(self, path)

x = directory(testdir)
input()
