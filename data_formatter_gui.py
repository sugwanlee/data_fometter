# 필요한 도구들을 가져옵니다
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                           QWidget, QPushButton, QFileDialog, QMessageBox,
                           QHBoxLayout, QTextEdit, QSplitter, QFrame)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon
import pandas as pd
from data_formatter import format_data
from datetime import datetime

class DragDropWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.output_dir = None
        self.conversion_history = []  # 변환 이력 저장
        self.initUI()
        
    def initUI(self):
        # 메인 윈도우 설정
        self.setWindowTitle('데이터 포맷터')
        self.setGeometry(100, 100, 800, 600)
        
        # 아이콘 설정
        if getattr(sys, 'frozen', False):
            # 실행 파일로 실행될 때
            application_path = sys._MEIPASS
        else:
            # Python 스크립트로 실행될 때
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        icon_path = os.path.join(application_path, 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 상단 영역 (입력/설정)
        top_frame = QFrame()
        top_frame.setFrameStyle(QFrame.StyledPanel)
        top_layout = QVBoxLayout(top_frame)
        
        # 드래그 앤 드롭 영역
        self.drop_label = QLabel('여기에 파일들을 드래그하세요\n(CSV 또는 Excel 파일들)')
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                background-color: #f8f9fa;
                font-size: 14px;
            }
        """)
        top_layout.addWidget(self.drop_label)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        
        # 파일 선택 버튼
        self.select_button = QPushButton('파일 선택하기')
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.select_button.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_button)
        
        # 출력 폴더 선택 버튼
        self.output_dir_button = QPushButton('출력 폴더 선택하기')
        self.output_dir_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.output_dir_button.clicked.connect(self.select_output_dir)
        button_layout.addWidget(self.output_dir_button)
        
        top_layout.addLayout(button_layout)
        
        # 출력 폴더 경로 표시 레이블
        self.output_dir_label = QLabel('출력 폴더: 기본값 (입력 파일과 같은 위치)')
        self.output_dir_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.output_dir_label)
        
        # 상태 표시 레이블
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.status_label)
        
        main_layout.addWidget(top_frame)
        
        # 하단 영역 (변환 이력)
        bottom_frame = QFrame()
        bottom_frame.setFrameStyle(QFrame.StyledPanel)
        bottom_layout = QVBoxLayout(bottom_frame)
        
        # 변환 이력 레이블
        history_label = QLabel('변환 이력')
        history_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        bottom_layout.addWidget(history_label)
        
        # 변환 이력 표시 영역
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        bottom_layout.addWidget(self.history_text)
        
        main_layout.addWidget(bottom_frame)
        
        # 드래그 앤 드롭 활성화
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
            self.drop_label.setStyleSheet("""
                QLabel {
                    border: 2px dashed #007bff;
                    border-radius: 5px;
                    padding: 20px;
                    background-color: #e9ecef;
                    font-size: 14px;
                }
            """)
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                background-color: #f8f9fa;
                font-size: 14px;
            }
        """)
            
    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.process_files(files)
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                background-color: #f8f9fa;
                font-size: 14px;
            }
        """)
        
    def select_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "파일 선택",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*.*)"
        )
        if file_paths:
            self.process_files(file_paths)
            
    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "출력 폴더 선택",
            "",
            QFileDialog.ShowDirsOnly
        )
        if dir_path:
            self.output_dir = dir_path
            self.output_dir_label.setText(f'출력 폴더: {dir_path}')
            
    def add_to_history(self, file_path, output_path, status, error=None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        history_entry = f"[{timestamp}] {os.path.basename(file_path)} → {os.path.basename(output_path)}"
        if status == "success":
            history_entry += " ✅"
        else:
            history_entry += f" ❌ ({error})"
        self.conversion_history.append(history_entry)
        self.history_text.setText("\n".join(self.conversion_history))
        self.history_text.verticalScrollBar().setValue(
            self.history_text.verticalScrollBar().maximum()
        )
        
    def process_files(self, file_paths):
        try:
            processed_files = []
            failed_files = []
            
            for file_path in file_paths:
                # 파일 확장자 확인
                file_extension = os.path.splitext(file_path)[1].lower()
                if file_extension not in ['.xlsx', '.xls', '.csv']:
                    failed_files.append((file_path, "지원하지 않는 파일 형식입니다."))
                    self.add_to_history(file_path, "", "error", "지원하지 않는 파일 형식입니다.")
                    continue
                
                try:
                    # 파일 처리
                    self.status_label.setText(f"파일 처리 중... ({len(processed_files) + 1}/{len(file_paths)})")
                    self.status_label.setStyleSheet("color: #666;")
                    QApplication.processEvents()
                    
                    output_path = format_data(file_path, self.output_dir)
                    processed_files.append(output_path)
                    self.add_to_history(file_path, output_path, "success")
                    
                except Exception as e:
                    failed_files.append((file_path, str(e)))
                    self.add_to_history(file_path, "", "error", str(e))
            
            # 결과 메시지 생성
            if processed_files:
                success_msg = f"✅ {len(processed_files)}개 파일 변환 완료!\n"
                if failed_files:
                    success_msg += f"\n❌ {len(failed_files)}개 파일 실패"
                self.status_label.setText(success_msg)
                self.status_label.setStyleSheet("color: #28a745;")
                
                # 결과 파일이 있는 폴더 열기
                if processed_files:
                    os.system(f"open {os.path.dirname(processed_files[0])}")
            
            # 실패한 파일이 있으면 오류 메시지 표시
            if failed_files:
                error_msg = "다음 파일들에서 오류가 발생했습니다:\n\n"
                for file_path, error in failed_files:
                    error_msg += f"- {os.path.basename(file_path)}: {error}\n"
                QMessageBox.warning(self, "일부 파일 처리 실패", error_msg)
            
        except Exception as e:
            # 전체 처리 중 오류 발생
            self.status_label.setText(f"❌ 오류 발생: {str(e)}")
            self.status_label.setStyleSheet("color: #dc3545;")
            QMessageBox.critical(self, "오류", str(e))

def main():
    app = QApplication(sys.argv)
    window = DragDropWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 