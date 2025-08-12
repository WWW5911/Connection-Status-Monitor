
from PyQt5.QtWidgets import QRadioButton, QButtonGroup, QHBoxLayout, QWidget

class qRadioButtonGroup(QWidget):
    def __init__(self, button_num: int, text: list):
        super().__init__()

        # 檢查數量和文字是否一致
        if len(text) != button_num:
            raise ValueError("text 列表長度必須等於 button_num")

        self.layout = QHBoxLayout(self)  # 用垂直排版放 Radio Button
        self.group = QButtonGroup(self)  # 建立按鈕群組（互斥）
        self.click_fn = self.tmp_function


        self.buttons = []  # 存放所有 QRadioButton 物件

        for i in range(button_num):
            btn = QRadioButton(text[i])
            self.layout.addWidget(btn)
            self.group.addButton(btn, i)  # 指定 ID
            self.buttons.append(btn)

        # 預設選第一個
        if self.buttons:
            self.buttons[0].setChecked(True)

        # 連接信號到 slot（方法）
        self.group.buttonClicked[int].connect(self.on_button_clicked)

    def get_selected_id(self):
        """取得目前選中的按鈕 ID"""
        return self.group.checkedId()

    def get_selected_text(self):
        """取得目前選中的按鈕文字"""
        btn = self.group.checkedButton()
        return btn.text() if btn else None
    
    def on_button_clicked(self, id):
        print(f"按下按鈕 ID={id}, 文字={self.buttons[id].text()}")
        # 在這裡呼叫你想要的特定 function
        self.click_fn(self, id)

    def tmp_function(self, id):
        # 依據 id 做特定處理
        print(f"執行特定函式，處理按鈕 {id}")
