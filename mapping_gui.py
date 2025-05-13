import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, 
    QHBoxLayout, QWidget, QFileDialog, QLabel,
    QMessageBox
)
from PyQt6.QtCore import Qt
import subprocess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('CSV 파일 처리 프로그램')
        self.setGeometry(100, 100, 600, 200)

        # 메인 위젯과 레이아웃 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 파일 선택 영역
        file_layout = QHBoxLayout()
        self.file_label = QLabel('선택된 파일: 없음')
        self.file_label.setWordWrap(True)
        file_button = QPushButton('파일 선택')
        file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(file_button)
        layout.addLayout(file_layout)

        # 작업 버튼 영역
        button_layout = QHBoxLayout()
        download_button = QPushButton('파일 다운로드')
        download_button.clicked.connect(self.download_files)
        convert_button = QPushButton('링크 변환')
        convert_button.clicked.connect(self.convert_links)
        button_layout.addWidget(download_button)
        button_layout.addWidget(convert_button)
        layout.addLayout(button_layout)

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "CSV 파일 선택",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if file_name:
            self.file_label.setText(f'선택된 파일: {file_name}')
            self.selected_file = file_name

    def download_files(self):
        if not hasattr(self, 'selected_file'):
            QMessageBox.warning(self, '경고', '파일을 선택해주세요.')
            return
        
        try:
            # 파이썬 인터프리터 경로 가져오기
            python_executable = sys.executable
            
            # csv_file_download.py 실행
            process = subprocess.Popen(
                [python_executable, 'csv_file_download.py'],
                stdin=subprocess.PIPE,
                text=True
            )
            
            # 파일 경로 입력
            process.communicate(input=f"{self.selected_file}\n")
            
            QMessageBox.information(self, '알림', '다운로드가 시작되었습니다.\n터미널에서 진행 상황을 확인해주세요.')
            
        except Exception as e:
            QMessageBox.critical(self, '오류', f'오류가 발생했습니다:\n{str(e)}')

    def convert_links(self):
        if not hasattr(self, 'selected_file'):
            QMessageBox.warning(self, '경고', '파일을 선택해주세요.')
            return
        
        try:
            # 파이썬 인터프리터 경로 가져오기
            python_executable = sys.executable
            
            # csv_link_trans.py 실행
            process = subprocess.Popen(
                [python_executable, 'csv_link_trans.py'],
                stdin=subprocess.PIPE,
                text=True
            )
            
            # 파일 경로 입력
            process.communicate(input=f"{self.selected_file}\n")
            
            QMessageBox.information(self, '알림', '변환이 시작되었습니다.\n터미널에서 진행 상황을 확인해주세요.')
            
        except Exception as e:
            QMessageBox.critical(self, '오류', f'오류가 발생했습니다:\n{str(e)}')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
