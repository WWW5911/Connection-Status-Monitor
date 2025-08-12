import sys
import subprocess
import platform
import os
import re
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QHeaderView
from MplCanvas import MplCanvas
from QRB_group import qRadioButtonGroup
from ScrollableTable import ScrollableTable
from datetime import datetime


def ping_ip_english(ip, count=4):
    system = platform.system().lower()
    
    if system == "windows":
        # Windows：先切換英文碼頁 437，再執行 ping
        # chcp 437 && ping -n count ip
        cmd = f'chcp 437 && ping -n {count} {ip}'
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True  # Windows 下使用 shell=True 執行複合指令
        )
    else:
        # Linux/macOS：設定環境變數 LANG 強制英文
        env = os.environ.copy()
        env["LANG"] = "en_US.UTF-8"
        env["LC_ALL"] = "en_US.UTF-8"
        param = "-c"
        result = subprocess.run(
            ["ping", param, str(count), ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )

    status = "Reachable"
    if "timed out" in result.stdout:
        status = "Timed out"
        time = "4000"
    else:
        result_idx = 0
        toks = result.stdout.split("\n")
        for i in range(len(toks)):
            if "Reply from " in toks[i]:
                result_idx = i
                break
        if "time=" in toks[result_idx]:
            time = toks[result_idx].split("time=")[-1].split(" ")[0]
        else:
            time = "0.01ms"
    return [status, time]

STARTED = False
RunningFLAG = False
targetIP = "8.8.8.8"
class DataThread(QThread):
    new_data_signal = pyqtSignal(list)  # 發送新資料到主執行緒
    def __init__(self, table = None):
        super().__init__()
        self.time_sleep = 1
        if table is not None:
            self.table = table

    def run(self):
        global RunningFLAG
        count = 0
        while RunningFLAG:
            STARTED = True
            time.sleep(self.time_sleep)  
            count += 1
            # new_row = [f"項目 {count}", f"值 {count}", f"狀態 {count}"]
            data = ping_ip_english(targetIP, 1)
            now = datetime.now()  # 取得當地時間
            new_row = [now.strftime("%Y-%m-%d %H:%M:%S")] + data
            if data[0] == "Timed out":
                error_table.add_row_to_top([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Connect to IP: {targetIP}, Timed out"], resize=False)
            self.new_data_signal.emit(new_row)


            self.canvas.set_data(self.table.get_data())
            self.canvas.plot_with_data()

    def set_table(self, table):
        self.table = table
    def set_canvas(self, canvas):
        self.canvas = canvas
    def set_error_table(self, error_table):
        self.error_table = error_table 

    def set_time(self, value):
        self.time_sleep = value

    def set_start(self):
        global RunningFLAG, STARTED
        if not STARTED:
            RunningFLAG = True
            self.start()
        print("STart")

    def set_stop(self):
        global RunningFLAG, STARTED
        RunningFLAG = False
        STARTED = False
        print("STOP")



app = QApplication(sys.argv)
worker = DataThread()

# 建立一個視窗
window = QWidget()
window.setWindowTitle("Connection Status Monitor")  # 視窗標題
window.resize(820, 620)  # 設定大小


layout = QHBoxLayout()
IP_label = QLabel("Target IP: ")
addres = QLineEdit()
btnStart = QPushButton("Start")
btnStop = QPushButton("Stop")
btnClear = QPushButton("Clear")

btnStart.clicked.connect(worker.set_start)
btnStop.clicked.connect(worker.set_stop)
addres.editingFinished.connect(lambda: on_IP_edit_finished(addres))
addres.setPlaceholderText("8.8.8.8")
def on_IP_edit_finished(widget):
    global targetIP
    def is_valid_ip(ip):
        pattern = r'^((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.|$)){4}$'
        return bool(re.match(pattern, ip))
    
    if is_valid_ip(widget.text()):
        targetIP = widget.text()
        print(targetIP)
    else:
        error_table.add_row_to_top([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "IP format error"])

layout.addWidget(IP_label)
layout.addWidget(addres)
layout.addWidget(btnStart)
layout.addWidget(btnStop)
layout.addWidget(btnClear)

layoutV = QVBoxLayout()


radio_group = qRadioButtonGroup(3, ["Every 1 second", "Every 5 seconds", "Every 30 seconds"])
radio_group.time_interval = 1
def set_time_interval(self, id):
    global worker
    timelist = [1, 5, 30]
    self.time_interval = timelist[id]
    worker.set_time(self.time_interval)

radio_group.click_fn = set_time_interval

rg_plot = qRadioButtonGroup(2, ["Bar chart", "Line chart"])


canvas = MplCanvas(width=5, height=4, dpi=100)
canvas.plot_with_data()
canvas.setMinimumWidth(500)
# canvas.plot_example()
layoutV.addLayout(layout)
layoutV.addWidget(radio_group)
layoutV.addWidget(rg_plot)

def set_plot(self, id):
    global worker
    if id == 0:
        canvas.set_plot_bar()
    if id == 1:
        canvas.set_plot_line()

rg_plot.click_fn = set_plot

s_table = ScrollableTable(rows=20, columns=3, headers = ["Date", "Status", "Time"]) # time, status, ms
s_table.set_init(["                                         ", "          ", "   "])
worker.set_table(s_table)
worker.set_canvas(canvas)
btnClear.clicked.connect(s_table.clear)

layout_result_panel = QHBoxLayout()
layout_result_panel.addWidget(canvas)
layout_result_panel.addWidget(s_table)

layoutV.addLayout(layout_result_panel)

error_table = ScrollableTable(rows=50, columns=2, headers = ["Date", "Message"])
error_table.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
error_table.table.horizontalHeader().setVisible(False)
error_table.setFixedHeight(120)
worker.set_error_table(error_table)

layoutV.addWidget(error_table)


layoutV.setStretch(0, 0)  
layoutV.setStretch(1, 0)  
layoutV.setStretch(2, 1)  # canvas 可伸縮
layoutV.setStretch(3, 0)  

window.setLayout(layoutV)


# 啟動 Thread
worker.new_data_signal.connect(s_table.add_row_to_top)
worker.start()
window.show()

# 進入事件迴圈
sys.exit(app.exec_())