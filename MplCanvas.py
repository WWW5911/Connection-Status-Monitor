import matplotlib
matplotlib.use('Qt5Agg')  # 使用 PyQt5 介面

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Patch
import seaborn as sns

import numpy as np
import re
from datetime import datetime

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)  # 建立一個子圖
        self.data = [[datetime.now().timestamp(),1,"0ms"], [datetime.now().timestamp(),0,"0ms"]]
        self.plot = "bar"
        super().__init__(self.fig)

    def set_data(self, data:list):
        for i in range(len(data)-1, -1, -1):
            if "            " in data[i][0] or len(data[i][0]) == 0:
                data.pop(i)
            else:
                data[i][0] = datetime.strptime(data[i][0], "%Y-%m-%d %H:%M:%S").timestamp()

        self.data = data


    def plot_with_data(self):
        x = []
        y = []
        label = []
        min_time = 1e20
        for instence in self.data:
            try:
                tmp = int(re.search(r'\d+', instence[2]).group())
                min_time = min(min_time, instence[0])
                label.append(1 if instence[1] == "Reachable" else 0)
                x.append(instence[0])
                y.append(tmp)
            except:
                print(instence)
        x = np.array(x) - min_time

        # 套用 seaborn 另一種風格，這裡用 'ticks'
        sns.set_theme(style="ticks")


        morandi_colors = {
            1: "#86C166",  # （Reachable）
            0: "#DB4D6D"   # （Not Reachable）
        }

        colors = [morandi_colors[l] for l in label]

        self.axes.clear()
        if self.plot == "bar":
            bars = self.axes.bar(x, y, color=colors, edgecolor='#565656', alpha=0.85)
        elif self.plot == "line":
            self.axes.plot(x, y, color=morandi_colors[1])
            x_notReach = [xi for xi, li in zip(x, label) if li == 0]
            y_notReach = [yi for yi, li in zip(y, label) if li == 0]
            c_notReach = [ci for ci, li in zip(colors, label) if li == 0]

            self.axes.bar(x_notReach, y_notReach, color=c_notReach, edgecolor='#565656', alpha=0.85)

        self.axes.set_title('Reachability Status Over Time', fontsize=14, fontweight='bold', color='#444444')
        self.axes.set_xlabel('Time (seconds)', fontsize=12, color='#666666')
        self.axes.set_ylabel('Round-Trip Time', fontsize=12, color='#666666')

        # 加邊框，搭配ticks風格
        for spine in self.axes.spines.values():
            spine.set_visible(True)
            spine.set_color('#888888')

        # 加輕微網格
        self.axes.grid(axis='y', linestyle='--', alpha=0.4, color='#AAAAAA')

        legend_elements = [Patch(facecolor=morandi_colors[1], edgecolor='#565656', label='Reachable'),
                        Patch(facecolor=morandi_colors[0], edgecolor='#565656', label='Not Reachable')]
        self.axes.legend(handles=legend_elements, frameon=False, fontsize=11, loc = "upper right")
        self.fig.tight_layout()
        self.draw()

    def set_plot_bar(self):
        self.plot = "bar"
    
    def set_plot_line(self):
        self.plot = "line"

    def plot_example(self):
        # 畫一條 sine 曲線
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        self.axes.clear()
        self.axes.plot(x, y)
        self.axes.set_title("Sine Wave")
        self.draw()