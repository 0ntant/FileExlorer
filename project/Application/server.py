import socket

class Server:
    def __init__(self,file_model):
     
        self.HOST = socket.gethostbyname(socket.gethostname())
        self.PORT = 9595  
        self.file_model = file_model
       
    def server_start(self, name_th):
        print('Start thread {}'.format(name_th))
        self.s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.bind((self.HOST,self.PORT))            
            self.s.listen()            
            print('server starts on {}:{}'.format(self.HOST,self.PORT))            
            while True:                     
                self.client_sock, client_addr = self.s.accept()                                              
                print('Connection {}'.format(client_addr))                
                while True:
                    try:
                        client_data = self.client_sock.recv(1024)                          
                        data_for_client = 'Error'
                        if not client_data:
                            client_sock.close()
                            break
                        client_data = client_data.decode()                        
                        
                        print('Client data: {}'.format(client_data))
                        
                        if client_data == 'Disconnect':
                            client_sock.close()
                            break
                        elif client_data == 'File list':
                            data_for_client = self.file_list()
                        elif client_data == 'Cur dir':
                            data_for_client = self.cur_dir()  
                        elif client_data == 'Connection check':
                            data_for_client = 'Connection: OK'
                        elif client_data == 'Ch dir':                            
                            data_for_client = self.ch_dir()
                        elif client_data == 'Download':
                            self.download()
                            data_for_client = 'Done'       
                        elif client_data == 'Cr file':
                            data_for_client = self.create_file()
                        elif client_data == 'Ch file ex':
                            data_for_client = self.check_file_exist()
                        elif client_data == 'Del file':
                            data_for_client = self.delete_file()
                        elif client_data == 'Cr dir':
                            data_for_client = self.create_folder()
                        elif client_data == 'Ren file':
                            data_for_client = self.rename_file()
                        elif client_data == 'Del dir':
                            data_for_client = self.delete_dir()
                        elif client_data == 'Cp file':
                            data_for_client = self.copy_file()
                            
                        self.client_sock.sendall('[BEGIN]{}[END]'.format(data_for_client).encode())          
                    except:
                        self.client_sock.close()
                        break
        except:
            print('Server stop')
            self.s.close()
            return
    
    def download(self):       
        file_name = self.client_sock.recv(1024).decode()
        print(file_name)
        file = self.file_model.read_file_bin_mode(file_name)
        if file:
            self.client_sock.sendall('[BEGIN]'.encode())
            self.client_sock.sendall(file)
            self.client_sock.sendall('[END]'.encode())
            self.client_sock.recv(1024)  
        else:
            self.client_sock.send(b'[ERROR]')
        return file
    
    def cur_dir(self):
        return self.file_model.read_cur_dir() 
    
    def ch_dir(self):
        path = self.client_sock.recv(1024).decode()                            
        self.file_model.ch_dir(path)                            
        data_for_client = 'Commad: done'  
        return data_for_client        
        
    def file_list(self):
        return ''.join(self.file_list_for_client())
        
    def server_stop(self):   
        if  hasattr(self, 'client_sock') and (self.client_sock.fileno() != -1):
            self.client_sock.close()
        self.s.close()
        
    def file_list_for_client(self):
        data = self.file_model.read_file_list()  
        data_for_client = []
        if (data != []):                                                
            for row in range(0,len(data)):     
                str_data = ''         
                for column in data[row]: 
                    str_data = str_data + str(data[row][column]) +'?'              
                data_for_client.append('{}|'.format(str_data))               
        return data_for_client
        
    def create_file(self):        
        file_name = self.client_sock.recv(1024).decode()
        file_name_list = file_name.split('|')
        try:
            self.file_model.create_file(file_name_list[0],file_name_list[1],file_name_list[2])
            return 'Done'
        except:
            return 'Error'
            
    def check_file_exist(self):
       
        file_name = self.client_sock.recv(1024).decode()
        if self.file_model.check_file_exist(file_name):           
            return 'True' 
        return 'False'
        
    def delete_file(self):
        try:
            file_name = self.client_sock.recv(1024).decode()
            self.file_model.delete_file(file_name)            
            return 'Done'
        except:
            return 'Error'
        
    def create_folder(self):
        try:
            file_name = self.client_sock.recv(1024).decode()
            self.file_model.create_folder(file_name)
            return 'Done'
        except:
            return 'Error'
        
    def rename_file(self):
        try:    
            client_data = self.client_sock.recv(1024).decode()
            client_data_list = client_data.split('|')
            print(client_data_list)
            self.file_model.rename_file(client_data_list[0],client_data_list[1])
            return 'Done'
        except:
            return 'Error'
        
    def delete_dir(self):
        try:
            path = self.client_sock.recv(1024).decode()
            self.file_model.delete_dir(path)
            return 'Done'
        except:
            return 'Error'
        
    def copy_file(self):
        try:
            client_data = self.client_sock.recv(1024).decode()
            client_data_list = client_data.split('|')
            self.file_model.copy_file(client_data_list[0],client_data_list[1],client_data_list[2])
            return 'Done'
        except:
            return 'Error'
        