import os
import shutil
from shutil import copyfile,copytree

class FileModel:

    def __init__(self):
        self.file_list = self.read_file_list()
        self.cur_dir   = self.read_cur_dir()        
    
    def read_file_list(self,path='.'):
        file_list = []
        with os.scandir(path) as dir_content:
            file_info = {}
            for file in dir_content:
                file_info = {
                    'Mode' : file.stat().st_mode,
                    'Name'    : file.name,
                    'Ext'     : os.path.splitext(file.name)[1],
                    'Mode time' : file.stat().st_mtime,
                    'Access time' : file.stat().st_atime,
                    'Size' : file.stat().st_size,
                }               
                file_list.append(file_info)
        return file_list        
    
    def read_cur_dir(self):
        return os.getcwd()
        
    def creat_file_alt(self, filename, data):
        with open(filename, 'w') as file:
            file.write(data)
    
    def read_file(self, filename):
        with open(filename, r) as file:
            return file.read()
    
    def read_file_bin_mode(self,filename):
        with open(filename,'rb') as file:
            return file.read()

    def create_bin_file(self,filename,data):
        with open(filename, 'wb') as file:
            file.write(data)

    def create_file(self,filename,data='',ext=''):
        if ext != '':
            ext = '.' + ext
        with open(filename+ext, 'w') as file:
            file.write(data)              
        
    def ch_dir(self,path):        
        return os.chdir(path)
    
    def delete_file(self,filename):
        return os.remove(filename)
        
    def delete_dir(self,path):
        shutil.rmtree(path)
    
    def os_command(self, command):
        os.system(command)
        
    def rename_file(self,last_name, new_name):
        file_list = last_name.split('.')
        if len(file_list) == 1:
           os.rename(last_name,new_name)
        else:
            new_file_list = new_name.split('.')
            if (len(new_file_list)==1):                
                os.rename(last_name, new_file_list[0]+'.'+file_list[1])
            else:
                os.rename(last_name, new_file_list[0]+'.'+new_file_list[1])
    
    def create_folder(self,path):
        os.mkdir(path)
        
    def check_file_exist(self, filename):
        if os.path.isfile(filename):
            return True
        return False    
        
    def copy_file(self, file, new_file ,ext):        
        if ext == '':
            copytree(file,new_file)
        else:
            copyfile(file,new_file)       
