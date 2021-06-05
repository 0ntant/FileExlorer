import socket

class Client:
    def __init__(self,HOST,file_model,file_root):    
       
        PORT = 9595
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_model = file_model
        self.file_root = file_root
        try:
            self.file_model.create_folder('{}\\{}'.format(file_root,'download'))
            self.file_model.create_folder('{}\\{}'.format(file_root,'tmp'))            
        except:
            pass
        try:
            self.s.connect((HOST,PORT))            
        except:           
            return None
    
    def disconnect(self):
        command = 'Disconnect'
        self.s.send(command.encode())
        self.s.close()
        
    def connection_check(self):
        try:
            self.s.send('Connection check'.encode())
            con_check = self.s.recv(1024)            
            con_check= con_check.decode().replace('[BEGIN]','').replace('[END]','')
            if con_check != 'Connection: OK':
                raise Exception('Connection fail')
            return True        
        except:           
            return False
            
    def read_file_list(self):
        try:
            command = 'File list'
            self.s.send(command.encode())
            data_from_server = self.s.recv(1024).decode()            
            while not '[END]' in data_from_server:
                data_from_server = data_from_server + self.s.recv(1024).decode()     
            data_from_server = self.file_list_handler(data_from_server)
            return data_from_server
        except:
            print('Read file from server failed')
            
    def file_list_handler(self,data_from_server):
        data_from_server = data_from_server.replace('[BEGIN]','').replace('[END]','')
        data_from_server_list = data_from_server.split('|')
        del data_from_server_list[-1]
        handled_data = []     
        for row in data_from_server_list:
            file_info = {}
            row_list = row.split('?')
            file_info = {
                'Mode' : int(row_list[0]),
                'Name' : row_list[1],
                'Ext'  : row_list[2],
                'Mode time': float(row_list[3]),
                'Access time' : float(row_list[4]),
                'Size': int(row_list[5]),
            }
            handled_data.append(file_info)          
        return handled_data    
        
    def read_cur_dir(self):
        try:
            command = 'Cur dir'
            self.s.send(command.encode())
            data_from_server = self.s.recv(1024).decode()
            if data_from_server:
                while not '[END]' in data_from_server:
                    data_from_server = data_from_server + self.s.recv(1024).decode()
                data_from_server = data_from_server.replace('[BEGIN]','').replace('[END]','')                
                return data_from_server
        except:
            print('Fail read current dir from server')
    
    def ch_dir(self,path):       
        try:
            print('to server : '+path)
            command = 'Ch dir'
            self.s.send(command.encode())
            self.s.send(path.encode())
            data_from_server = self.s.recv(1024).decode()
            data_from_server = data_from_server.replace('[BEGIN]','').replace('[END]','') 
            if data_from_server == 'Commad: done':
                return
            else:
                raise Exception('Fail send command to server')
        except:
            print('Fail send command to server')     
                       
    def create_file(self,filename,data='',ext=''):
        command = 'Cr file'
        self.s.send(command.encode())
        self.s.send('{}|{}|{}'.format(filename,data,ext).encode())
        res = self.s.recv(1024)
        if res == b'[BEGIN]Done[END]':
            return True
        else:
            raise Exception('Failure creating file on server')
            
    def delete_file(self,filename):
        command = b'Del file'
        self.s.send(command)
        self.s.send(filename.encode())
        res = self.s.recv(1024)
        if res == b'[BEGIN]Done[END]':
            return True
        else:
            raise Exception('Fail to del file from server')
    
    def delete_dir(self,path):
        command = b'Del dir'
        self.s.send(command)
        self.s.send(path.encode())
        res = self.s.recv(1024)
        if res == b'[BEGIN]Done[END]':
            return True
        else:
            raise Exception('Fail to del file from server')
    
    def os_command(self, command):
        pass
        
    def rename_file(self,last_name, new_name):
        command = b'Ren file'
        self.s.send(command)
        self.s.send('{}|{}'.format(last_name,new_name).encode())
        res = self.s.recv(1024)
        if res == b'[BEGIN]Done[END]':
            return True
        else:
            return Exception('Failure rename file on server')
            
    def create_folder(self,path):
        command = b'Cr dir'
        self.s.send(command)
        self.s.send(path.encode())
        res = self.s.recv(1024)
        if res == b'[BEGIN]Done[END]':
            return True
        else:
            return Exception('Fail to create dir on server')
            
    def check_file_exist(self, filename):
        command = b'Ch file ex'
        self.s.send(command)
        self.s.send(filename.encode())
        res = self.s.recv(1024)      
        if res == b'[BEGIN]True[END]':
            return True
        return False
        
    def copy_file(self, file, new_file ,ext):        
        command = b'Cp file'
        self.s.send(command)
        self.s.send('{}|{}|{}'.format(file,new_file,ext).encode())
        res = self.s.recv(1024)
        if res == b'[BEGIN]Done[END]':
            return True
        else:
            return Exception('Fail to copy file on server')        
        
    def download(self, file_name):
        try:
            command = 'Download'
            self.s.send(command.encode())
            self.s.send(file_name.encode())
            file_from_server = self.s.recv(7).decode()   
            if file_from_server == '[BEGIN]':
                bytes_from_server = b''
                while True:
                    file_from_server = self.s.recv(1024)
                    bytes_from_server = bytes_from_server + file_from_server                
                    if b'[END]' in file_from_server:
                        break
                self.s.send(b'Done')  
                bytes_from_server = bytes_from_server[:-5]
                print(bytes_from_server)
                file_from_server = self.s.recv(1024).decode()               
                path = '{}\\{}\\{}'.format(self.file_root,'download',file_name)
                self.file_model.create_bin_file(path,bytes_from_server)                
            else:
                self.s.recv(1024)
        except:
            print('Fail download from server')
            