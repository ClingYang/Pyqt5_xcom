import sys
import time
import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QTextCursor,QColor
from PyQt5.QtCore import QThread, QTimer
import Ui_serial
import threading
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

from Serial_thread import Serial_Qthread_function

class SerialFrom(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_serial.Ui_Serial()
        self.ui.setupUi(self)
        self.Interface_init()
        self.UI_Init()
     
        print("主线程ID:", threading.current_thread().ident)

        # 创建一个 QThread 对象
        self.Serial_Qthread = QThread()
        
        # 创建 Serial_Qthread_function 的实例
        self.Serial_Qthread_function = Serial_Qthread_function()
        
        # 将 Serial_Qthread_function 实例移动到 QThread
        self.Serial_Qthread_function.moveToThread(self.Serial_Qthread)
        
        # 启动 QThread
        self.Serial_Qthread.start()
        
        # 将信号连接到 SerialInit_function 槽
        self.Serial_Qthread_function.signal_Serialstart_function.connect(self.Serial_Qthread_function.SerialInit_function)

        # 发射信号以启动 SerialInit_function
        self.Serial_Qthread_function.signal_Serialstart_function.emit()
        self.Serial_Qthread_function.signal_pushButton_Open.connect(self.Serial_Qthread_function.solt_signal_pushButton_Open)
        self.Serial_Qthread_function.signal_pushButton_Open_flage.connect(self.solt_signal_pushButton_Open_flage)
        self.Serial_Qthread_function.signal_Serial_Receive_Data.connect(self.solt_signal_Serial_Receive_Data)
        self.Serial_Qthread_function.signal_RTS.connect(self.Serial_Qthread_function.slot_signal_RTS)
        self.Serial_Qthread_function.signal_DTR.connect(self.Serial_Qthread_function.slot_signal_DTR)
        self.Serial_Qthread_function.signal_Send_data.connect(self.Serial_Qthread_function.slot_signal_Send_data)
        self.Serial_Qthread_function.signal_Send_data_length.connect(self.slot_signal_Send_data_length)
        self.port_name = []
        # 定时器扫描串口
        self.time_scan = QTimer()
        self.time_scan.timeout.connect(self.TimeOut_Scan)
        self.time_scan.start(1000)

        #
        self.time_send = QTimer()
        self.time_send.timeout.connect(self.TimeOut_Send)
        self.Receiverlenght = 0
        self.Sendlenght     = 0

    def TimeOut_Scan(self):
        # print("定时器超时")
        available_port = QSerialPortInfo.availablePorts() 
        new_port = []
        for port in available_port:
            new_port.append(port.portName())
        if len(self.port_name)!= len(new_port):
            self.port_name = new_port
            # print(self.port_name)
            self.ui.comboBox_Com.clear()
            self.ui.comboBox_Com.addItems(self.port_name)

    def TimeOut_Send(self):
        self.pushButton_Send()
    def Interface_init(self):
        # 初始化界面
        self.setWindowTitle("PYQT串口工具")
        self.setGeometry(100, 100, 700, 520)
        self.ui.comboBox_Com.clear()
        self.ui.comboBox_Baud.clear()
        self.ui.comboBox_Stop.clear()
        self.ui.comboBox_Data.clear()
        self.ui.comboBox_Check.clear()
        # 设置波特率选项
        self.BaudRate = ('9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600')
        # 设置停止位选项
        self.StopBits =('1', '1.5', '2')
        # 设置数据位选项
        self.DataBits = ('8', '7','5', '6')
        # 设置校验位选项
        self.CheckBits = ('None',  'Odd', 'Even')
        # 将选项添加到对应的下拉框中
        self.ui.comboBox_Baud.addItems(self.BaudRate)
        self.ui.comboBox_Stop.addItems(self.StopBits)
        self.ui.comboBox_Data.addItems(self.DataBits)
        self.ui.comboBox_Check.addItems(self.CheckBits)
        self.ui.checkBox_RTS.stateChanged.connect(self.checkBox_RTS)
        self.ui.checkBox_DTR.stateChanged.connect(self.checkBox_DTR)
        self.ui.checkBox_HexSend.stateChanged.connect(self.checkBox_HexSend)
        self.ui.pushButton_Send.clicked.connect(self.pushButton_Send)
        self.ui.checkBox_TimeSend.stateChanged.connect(self.checkBox_TimeSend)
        self.ui.lineEdit_IntervalTime.setText("1000")
        self.ui.pushButton_SendClean.clicked.connect(self.pushButton_SendClean)
        self.ui.pushButton_ReceiveClean.clicked.connect(self.pushButton_ReceiveClean)
        
        
    def UI_Init(self):
        self.ui.pushButton_Open.clicked.connect(self.pushButton_Open)

    def pushButton_Open(self):
        self.set_parameter = {}
        self.set_parameter['comboBox_Com'] = self.ui.comboBox_Com.currentText()
        self.set_parameter['comboBox_Baud'] = self.ui.comboBox_Baud.currentText()
        self.set_parameter['comboBox_Stop'] = self.ui.comboBox_Stop.currentText()
        self.set_parameter['comboBox_Data'] = self.ui.comboBox_Data.currentText()
        self.set_parameter['comboBox_Check'] = self.ui.comboBox_Check.currentText()
        self.Serial_Qthread_function.signal_pushButton_Open.emit(self.set_parameter)
    def solt_signal_pushButton_Open_flage(self,sate):
        print("串口打开状态",sate)
        if sate == 0:
            qtw.QMessageBox.warning(self,"错误信息","串口已被占用，打开失败")
        elif sate == 1:
            self.ui.pushButton_Open.setStyleSheet("color:red")
            self.ui.pushButton_Open.setText("关闭串口")
            self.time_scan.stop()
        elif sate == 2:
            self.ui.pushButton_Open.setStyleSheet("color:black")
            self.ui.pushButton_Open.setText("打开串口")
            self.time_scan.start(1000)
        else:
            pass
    def solt_signal_Serial_Receive_Data(self,data):

        self.Receiverlenght = self.Receiverlenght+ len(data)
        self.ui.label_RX.setText("接收:"+str(self.Receiverlenght))
        # print(data)
        if self.ui.checkBox_Timemark.checkState():
            timer_str ="\r\n" + time.strftime("%Y-%m-%d %H:%M:%S:", time.localtime()) + "\r\n"
            self.ui.textEdit_Receive.setTextColor(QColor(255,100,100))
            self.ui.textEdit_Receive.insertPlainText(timer_str)
            self.ui.textEdit_Receive.setTextColor(QColor(0,0,0))
            
        Byte_data = bytes(data)
        if self.ui.checkBox_HexView.checkState():
            View_data = ''
            for i in range(0,len(Byte_data)):
                View_data = View_data +'{:02x}'.format(Byte_data[i]) + ''
            self.ui.textEdit_Receive.insertPlainText(View_data)
        else :
            self.ui.textEdit_Receive.insertPlainText(Byte_data.decode("utf-8","ignore"))
        self.ui.textEdit_Receive.moveCursor(QTextCursor.MoveOperation.End)

    def checkBox_RTS(self,state):
       self.Serial_Qthread_function.signal_RTS.emit(state)

    def checkBox_DTR(self,state):
        self.Serial_Qthread_function.signal_DTR.emit(state)

    def checkBox_HexSend(self,state):
        print("16j")
        if 2 == state:
            send_text = self.ui.textEdit_Send.toPlainText()
            Byte_text = str.encode(send_text)
            View_data = '' 
            for i in range(0,len(Byte_text)):
                 View_data = View_data +'{:02x}'.format(Byte_text[i]) + ' '
            self.ui.textEdit_Send.setText(View_data)
  
        else :
            send_list = []
            send_text = self.ui.textEdit_Send.toPlainText()
            while send_text != '' :
                try:
                    num = int(send_text[0:2],16)
                except:
                    qtw.QMessageBox.warning(self,"错误信息","输入的数据不是16进制数据") 
                    return
                send_text = send_text[2:].strip()
                send_list.append(num)

            input_s = bytes(send_list)
            self.ui.textEdit_Send.setText(input_s.decode("utf-8","ignore"))
    def pushButton_Send(self):
        print("点击发送按钮")
        send_data = {}
        send_data['Data'] = self.ui.textEdit_Send.toPlainText() + "\r\n"
        send_data['NewLine'] = self.ui.checkBox_NewLine.checkState()
        send_data['Data'] = self.ui.textEdit_Send.toPlainText() 
        send_data['Hex'] = self.ui.checkBox_HexSend.checkState()
        self.Serial_Qthread_function.signal_Send_data.emit(send_data)
    def checkBox_TimeSend(self,state):
        if 2 == state:
            tiem_data = self.ui.lineEdit_IntervalTime.text()
            self.time_send.start(int(tiem_data))
        else:
            self.time_send.stop()
    def pushButton_SendClean(self):
        self.Sendlenght=0
        self.ui.label_TX.setText("发送:"+str(self.Sendlenght))
        self.ui.textEdit_Send.clear()
        
    def pushButton_ReceiveClean(self):
        self.Receiverlenght=0
        self.ui.label_RX.setText("接收:"+str(self.Receiverlenght))
        self.ui.textEdit_Receive.clear()
        self.Sendlenght=0
        self.ui.label_TX.setText("发送:"+str(self.Sendlenght))
        self.ui.textEdit_Send.clear()
        
    def slot_signal_Send_data_length(self,length):
        self.Sendlenght = self.Sendlenght + length
        self.ui.label_TX.setText("发送:"+str(self.Sendlenght))



if __name__ == '__main__':
    # 创建应用程序对象
    app = qtw.QApplication(sys.argv)
    
    # 创建主窗口对象
    Window = SerialFrom()
    
    # 显示主窗口
    Window.show()
    
    # 进入应用程序主循环
    sys.exit(app.exec_())