import sys 
import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QThread, pyqtSignal,QObject
import threading
from time import sleep
from PyQt5.QtSerialPort import QSerialPort
class Serial_Qthread_function(QObject):
    signal_Serialstart_function       = pyqtSignal()
    signal_pushButton_Open            = pyqtSignal(object)
    signal_pushButton_Open_flage      = pyqtSignal(object)
    signal_Serial_Receive_Data        = pyqtSignal(object)
    signal_DTR                        = pyqtSignal(object)
    signal_RTS                        = pyqtSignal(object)
    signal_Send_data                  = pyqtSignal(object)
    signal_Send_data_length           = pyqtSignal(object)

    def __init__(self, parent = None):
        super(Serial_Qthread_function, self).__init__(parent)
        # 初始化时的线程ID
        print("初始化时候线程", threading.current_thread().ident)
        self.state = 0 #未打开  1串口已打开 2串口已关闭

    def slot_signal_DTR(self,state):
        print("DTR",state)
        if 2 == state:
            self.Serial.setDataTerminalReady(True)
        else :
            self.Serial.setDataTerminalReady(False)

    def slot_signal_RTS(self,state):
        print("RTS",state)
        if 2 == state:
            self.Serial.setRequestToSend(True)
        else :
            self.Serial.setRequestToSend(False)

    def solt_signal_pushButton_Open(self,paramter):
        if self.state == 0:
            print("按下打开串口按钮",paramter)
            self.Serial.setPortName(paramter['comboBox_Com'])
            self.Serial.setBaudRate(int(paramter['comboBox_Baud']))
            if paramter['comboBox_Stop'] == '1.5':
                self.Serial.setStopBits(3)
            else:
                self.Serial.setStopBits(int(paramter['comboBox_Stop']))

            self.Serial.setDataBits(int(paramter['comboBox_Data']))

            setParity = 0
            if paramter['comboBox_Check'] == 'None':
                setParity = 0
            elif paramter['comboBox_Check'] == 'Even':
                setParity = 2
            elif paramter['comboBox_Check'] == 'Odd':
                setParity = 3
            self.Serial.setParity(setParity)
           
            if self.Serial.open(QSerialPort.ReadWrite) == True:
                print("串口打开成功")
                self.state = 1
                self.signal_pushButton_Open_flage.emit(self.state)
            else :
                print("串口打开失败")
                self.signal_pushButton_Open_flage.emit(0)
        else :
            print("关闭串口")
            self.state = 0
            self.Serial.close()
            self.signal_pushButton_Open_flage.emit(2)


            
            # self.Serial.setParity(paramter['comboBox_Check'])
            
            # self.Serial.setFlowControl(paramter['comboBox_Flow'])

    def slot_signal_Send_data(self,send_data):
       
        if self.state != 1:
            return
        print("发送数据",send_data['Hex'],send_data['Data'])
        send_buff =''
        if send_data['Hex'] == 2:
            send_list = []
            send_text = send_data['Data']
            while send_text != '' :
                try:
                    num = int(send_text[0:2],16)
                except:
                    return
                send_text = send_text[2:].strip()
                send_list.append(num)
            # input_s = bytes(send_list).decode()
            input_s = bytes(send_list).decode('utf-8')  # 指定编码方式
            if send_data['NewLine']==2:
                send_buff = input_s + '\r\n'
            else: 
                send_buff = input_s
            
        else:
            if send_data['NewLine'] == 2:
                    send_buff = send_data['Data'] + '\r\n'
            else: 
                    send_buff = send_data['Data']
        Byte_data = str.encode(send_buff)
        self.Serial.write(Byte_data)
        
        self.signal_Send_data_length.emit(len(Byte_data))          


          
    def Serial_receive_data(self):
        # # 串口接收数据的槽函数
        # print("接收数据线程ID: ", threading.current_thread().ident)
       
        # # 读取串口数据
        # data = self.Serial.readAll()
        # print("接收数据",data)   
      self.signal_Serial_Receive_Data.emit(self.Serial.readAll())
      

    def SerialInit_function(self):
        # 模拟串口初始化的延迟
        sleep(2)
        # 打印当前运行的线程ID
        print("串口运行线程ID: ", threading.current_thread().ident)
        self.Serial  =  QSerialPort()
        self.Serial.readyRead.connect(self.Serial_receive_data)
    