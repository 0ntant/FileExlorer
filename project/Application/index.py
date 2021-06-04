import view
import model
import server
import client

from PyQt5 import QtCore, QtGui, QtWidgets, sip
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem , QMenu,QAction,QMessageBox

from datetime import datetime
import sys  
import threading

from functools import partial
from datetime import datetime
from collections import deque
            
class App(QtWidgets.QMainWindow, view.Ui_Dialog):
    def __init__(self):
        
        self.file_model = model.FileModel()
        
        super().__init__()
        self.setupUi(self)
        
        #conf
        self.new_dir  = 'New dir'
        self.new_file = 'New file'
        self.file_root = self.file_model.read_cur_dir()
        self.file_deque = deque()
                     
        #cur dir
        self.dirLineEdit.setText(self.file_model.read_cur_dir())
        #table      
        self.draw_table(self.data_for_table())        
              
        #chage directory
        self.dirLineEdit.editingFinished.connect(self.change_dir)        
               
        #open folder       
        self.tableWidget.itemDoubleClicked.connect(self.open_folder)
        
        #upper folder
        self.upButton.clicked.connect(self.upper_folder)
        
        #change file
        self.tableWidget.itemChanged.connect(self.file_rename)         
        
        #contex menu on right click
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.contex_menu_open)
        
        #get file name
        self.tableWidget.itemClicked.connect(self.get_file_name)
        
        #go back
        self.backButton.clicked.connect(self.last_directory)
        
        #start server
        self.startServerButton.clicked.connect(self.start_server)
        #stot server
        self.stopServerButton.clicked.connect(self.stop_server)
        self.stopServerButton.setEnabled(False)
        
        #connect 
        self.connectButton.clicked.connect(self.connect_to_server)
        #self.ipAddrLineEdit.setText('127.0.0.1')
        self.disconnectButton.setEnabled(False)
        
        #disconnect
        self.disconnectButton.clicked.connect(self.disconnect_from_server)
        
    def contex_menu_open(self,pos):
        context = QMenu(self)
        try:
            file_name = self.tableWidget.item(self.tableWidget.currentRow(),1).text()
            file_ext = self.tableWidget.item(self.tableWidget.currentRow(),2).text()                                                   
            #Actions                  
            delete = QAction('Delete', self)         
            delete.triggered.connect(self.delet_file_from_table)
            context.addAction(delete)            
            if file_ext != 'directory':        
                open_note = QAction('Note', self)
                open_note.triggered.connect(self.open_notepad)       
                context.addAction(open_note)                    
            
            copy = QAction('Copy', self)
            copy.triggered.connect(self.copy_file)
            context.addAction(copy)
            
             #Client Action 
            if hasattr(self, 'client'):
                download = QAction('Download', self)
                download.triggered.connect(self.download_from_server)
                context.addAction(download)
            
        except AttributeError:
            pass
        finally:
            #Create files
            create_file = context.addMenu('Create file')
            
            create_txt = QAction('.txt',self)
            create_py  = QAction('.py',self)
            
            create_txt.triggered.connect(partial(self.create_file, 'txt'))
            create_py.triggered.connect(partial(self.create_file,'py'))
            
            create_file.addAction(create_py)
            create_file.addAction(create_txt)        
            
            #create folder            
            create_dir = QAction('Create dir',self)
            create_dir.triggered.connect(self.create_directory)
            context.addAction(create_dir)
            
            #update
            update_dir = QAction('Update',self)
            update_dir.triggered.connect(self.update_directory)
            context.addAction(update_dir)     
           
            
            context.exec_(self.mapToGlobal(pos))       
    
    def download_from_server(self):
        self.tableWidget.blockSignals(True)
        file_name = self.tableWidget.item(self.tableWidget.currentRow(),1).text() 
        self.file_model.download(file_name)
        self.tableWidget.blockSignals(False)
        
    def disconnect_from_server(self):
        self.tableWidget.blockSignals(True)
        self.file_model.disconnect()
        self.file_model = model.FileModel()
        del self.client
        self.file_deque.clear()
        self.update_directory()
        
        self.disconnectButton.setEnabled(False)
        self.connectButton.setEnabled(True)
        
        self.tableWidget.blockSignals(False)
    
    def connect_to_server(self,file_model):
        self.tableWidget.blockSignals(True)
        ip_server_addr = self.ipAddrLineEdit.text()
        self.client = client.Client(ip_server_addr,self.file_model,self.file_root)
        if self.client != None and self.client.connection_check() == True:           
            self.file_model = self.client
            self.file_deque.clear()
            self.update_directory()
            self.disconnectButton.setEnabled(True)
            self.connectButton.setEnabled(False)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Can't connect to {}".format(ip_server_addr))            
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        self.tableWidget.blockSignals(False)
    
    def stop_server(self):
        self.tableWidget.blockSignals(True)   
        
        self.server.server_stop()
        self.ser_th.join()
        self.startServerButton.setEnabled(True)
        self.stopServerButton.setEnabled(False)
        self.tableWidget.blockSignals(False)
    
    def start_server(self):
        self.tableWidget.blockSignals(True)
        self.server = server.Server(self.file_model)
        
        self.startServerButton.setEnabled(False)
        self.stopServerButton.setEnabled(True)
        
        self.ser_th = threading.Thread(target=self.server.server_start, args=(1,), daemon = True)  
        self.ser_th.start()
        
       
        self.tableWidget.blockSignals(False)
    
    def change_directory(self, path):
        self.file_deque.append(self.file_model.read_cur_dir())
        self.file_model.ch_dir(path)        
    
    def copy_file(self,trigger, copy_name = ''):
        self.tableWidget.blockSignals(True)
        file_name = self.tableWidget.item(self.tableWidget.currentRow(),1).text()
        ext = self.tableWidget.item(self.tableWidget.currentRow(),2).text()
        try:        
            if ext == 'directory':
                ext = ''  
                new_name = file_name.split('.')[0]+copy_name
            else:
                new_name = file_name.split('.')[0]+copy_name+'.'+file_name.split('.')[1]            
            
            if self.file_model.check_file_exist(new_name):
                raise FileExistsError ('File exists') 
            
            self.file_model.copy_file(file_name,new_name,ext)
                
            self.update_directory()            
        except FileExistsError:          
            self.copy_file(trigger,copy_name = copy_name + ' copy')
        self.tableWidget.blockSignals(False)    
     
    
    def last_directory(self):
        self.tableWidget.blockSignals(True)
        if self.file_deque:        
            self.file_model.ch_dir(self.file_deque.pop())
            self.dirLineEdit.setText(self.file_model.read_cur_dir())
            self.draw_table(self.data_for_table())
        self.tableWidget.blockSignals(False)
        
    def update_directory(self):
        self.draw_table(self.data_for_table())
          
    def create_directory(self):       
        try:            
            self.file_model.create_folder(self.new_dir)
            self.new_dir = 'New dir'
            self.update_directory()
        except FileExistsError:
            self.new_dir = self.new_dir + ' copy'
            self.create_directory()
            
    def create_file(self,ext):
        try:  
            if self.file_model.check_file_exist(self.new_file+'.'+ext):
                raise FileExistsError ('File exists')                           
            self.file_model.create_file(self.new_file, ext = ext)
            self.new_file = 'New file'
            self.update_directory()
        except FileExistsError:
            self.new_file = self.new_file + ' copy'            
            self.create_file(ext)                    
                               
    def file_rename(self,item,copy_name= ''):       
       self.tableWidget.blockSignals(True)        
       try: 
           if self.file_name == '':
               self.file_name = 'New file'
           else:             
               if copy_name == '':
                    self.file_model.rename_file(self.file_name,item.text())                    
               else:
                    self.file_model.rename_file(self.file_name,self.file_name+copy_name) 
               self.draw_table(self.data_for_table())    
       except FileNotFoundError:            
            pass                
       except FileExistsError:
            self.file_model.rename_file(item,copy_name = copy_name + ' copy')
            self.draw_table(self.data_for_table())            
                
       self.tableWidget.blockSignals(False)    
    
    def get_file_name(self,item):      
        self.tableWidget.blockSignals(True)
        self.file_name = self.tableWidget.item(item.row(), 1).text()
        self.tableWidget.blockSignals(False)
        
    def upper_folder(self):
        self.tableWidget.blockSignals(True)
        curr_dir = self.file_model.read_cur_dir()
        dir_list = curr_dir.split('\\')
        upper_dir= ''       
        for i in range(0,len(dir_list)-1):
            upper_dir = '{}{}{}'.format(upper_dir , dir_list[i], '\\')    
        self.change_directory(upper_dir)
        self.dirLineEdit.setText(upper_dir)
        self.draw_table(self.data_for_table())
        self.tableWidget.blockSignals(False)        
        
    def open_folder(self):       
        self.tableWidget.blockSignals(True)
        file_name = self.tableWidget.item(self.tableWidget.currentRow(),1).text()
        file_ext  = self.tableWidget.item(self.tableWidget.currentRow(),2).text()        
        if file_ext == 'directory':           
            self.change_directory(file_name)
            self.dirLineEdit.setText(self.file_model.read_cur_dir())
            self.draw_table(self.data_for_table())  
            self.file_name = file_name       
        self.dirLineEdit.setText(self.file_model.read_cur_dir())  
        self.tableWidget.blockSignals(False)        
    
    def open_notepad(self):
         file_name =self.tableWidget.item(self.tableWidget.currentRow(),1).text()
         self.file_model.os_command("notepad.exe {}".format(file_name))
    
    def change_dir(self):        
        self.tableWidget.blockSignals(True)
        try:            
            self.change_directory(self.dirLineEdit.text())
            self.draw_table(self.data_for_table())
            self.dirLineEdit.setText(self.file_model.read_cur_dir())        
        except FileNotFoundError:
            self.dirLineEdit.setText(self.file_model.read_cur_dir())
        self.tableWidget.blockSignals(False)
        
    def delet_file_from_table(self):
        self.tableWidget.blockSignals(True)
        file_name = self.tableWidget.item(self.tableWidget.currentRow(),1).text()
        file_ext  = self.tableWidget.item(self.tableWidget.currentRow(),2).text()
        
        if file_ext != 'directory':
            self.file_model.delete_file(file_name)
        else:
            self.file_model.delete_dir(file_name)            
       
        self.tableWidget.removeRow(self.tableWidget.currentRow())
        self.tableWidget.blockSignals(False)
      
    def data_for_table(self):    
        table_data = []
        data = self.file_model.read_file_list()
        headers = []         
        if (data != []) and (data != None):            
            for key in data[0].keys():
                headers.append(key)                      
            for row in range(0,len(data)):     
                row_table_data = []           
                for column in data[row]: 
                    if (data[row]['Ext'] == ''):
                        data[row]['Ext'] = 'directory'
                    if (column == 'Mode time' or column == 'Access time'):
                        data[row][column] = self.convert_time(data[row][column])
                    row_table_data.append(data[row][column])               
                table_data.append(row_table_data)        
        else:
            headers = ['Mode','Name', 'Ext', 'Mode time','Access time', 'Size']            
        return (headers,table_data)
          
    def draw_table(self, data):
        self.tableWidget.blockSignals(True)
        if data[1] != []:        
            self.tableWidget.setColumnCount(len(data[1][0]))    
            self.tableWidget.setRowCount(len(data[1]))   
            for i in range(0,len(data[1])):
                for j in range(0,len(data[1][i])):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(data[1][i][j])))
        else:
             self.tableWidget.clear()
             self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(data[0])
        self.tableWidget.blockSignals(False)      
            
    def convert_time(self,timestamp):        
        d = datetime.utcfromtimestamp(timestamp)
        formated_date = d.strftime('%d %b %Y')
        return formated_date                                  
         
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = App()  
    window.show()  
    app.exec_()  

main()    
