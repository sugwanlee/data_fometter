import sys
import os
import csv
import requests
import mimetypes
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                           QWidget, QPushButton, QFileDialog, QMessageBox,
                           QHBoxLayout, QTextEdit, QSplitter, QFrame, QLineEdit)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon
import asyncio
from link_mapping import process_csv, is_file_url, normalize_url, upload_file_to_supabase, get_public_url

class LinkMappingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.output_file = None
        self.conversion_history = []
        self.initUI()
        
    def initUI(self):
        # 메인 윈도우 설정
        self.setWindowTitle('URL 매핑 도구')
        self.setGeometry(100, 100, 800, 600)
        
        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 파일 선택 영역
        file_frame = QFrame()
        file_frame.setFrameStyle(QFrame.StyledPanel)
        file_layout = QVBoxLayout(file_frame)
        
        # 입력 파일 선택
        input_layout = QHBoxLayout()
        self.input_label = QLabel('입력 파일:')
        self.input_path_label = QLabel('선택된 파일 없음')
        self.input_button = QPushButton('입력 파일 선택')
        self.input_button.clicked.connect(self.select_input_file)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_path_label)
        input_layout.addWidget(self.input_button)
        file_layout.addLayout(input_layout)
        
        # 출력 파일 선택
        output_layout = QHBoxLayout()
        self.output_label = QLabel('출력 파일:')
        self.output_path_label = QLabel('선택된 파일 없음')
        self.output_button = QPushButton('출력 파일 선택')
        self.output_button.clicked.connect(self.select_output_file)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_path_label)
        output_layout.addWidget(self.output_button)
        file_layout.addLayout(output_layout)
        
        # 변환 버튼
        self.convert_button = QPushButton('변환 시작')
        self.convert_button.setStyleSheet("""
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
        self.convert_button.clicked.connect(self.start_conversion)
        file_layout.addWidget(self.convert_button)
        
        # 상태 표시
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        file_layout.addWidget(self.status_label)
        
        main_layout.addWidget(file_frame)
        
        # 변환 이력 영역
        history_frame = QFrame()
        history_frame.setFrameStyle(QFrame.StyledPanel)
        history_layout = QVBoxLayout(history_frame)
        
        history_label = QLabel('변환 이력')
        history_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        history_layout.addWidget(history_label)
        
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
        history_layout.addWidget(self.history_text)
        
        main_layout.addWidget(history_frame)
        
    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "입력 CSV 파일 선택",
            "",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        if file_path:
            self.input_file = file_path
            self.input_path_label.setText(os.path.basename(file_path))
            
            # 자동으로 출력 파일 경로 설정
            if not self.output_file:
                dir_name = os.path.dirname(file_path)
                base_name = os.path.basename(file_path)
                name, ext = os.path.splitext(base_name)
                self.output_file = os.path.join(dir_name, f"updated_{name}{ext}")
                self.output_path_label.setText(os.path.basename(self.output_file))
            
    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "출력 CSV 파일 선택",
            "",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        if file_path:
            self.output_file = file_path
            self.output_path_label.setText(os.path.basename(file_path))
            
    def add_to_history(self, message, status="info"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        history_entry = f"[{timestamp}] {message}"
        if status == "success":
            history_entry += " ✅"
        elif status == "error":
            history_entry += " ❌"
        self.conversion_history.append(history_entry)
        self.history_text.setText("\n".join(self.conversion_history))
        self.history_text.verticalScrollBar().setValue(
            self.history_text.verticalScrollBar().maximum()
        )
        
    async def process_file(self):
        if not self.input_file or not self.output_file:
            raise Exception("입력 파일과 출력 파일을 모두 선택해주세요.")
            
        # link_mapping.py의 함수들을 사용하여 파일 처리
        rows = []
        with open(self.input_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            
        if not rows:
            raise Exception("CSV 파일이 비어있습니다.")
            
        columns = rows[0].keys()
        file_columns = [
            col for col in columns 
            if any(is_file_url(row[col]) for row in rows)
        ]
        
        if not file_columns:
            raise Exception("bubble.io URL을 포함한 컬럼을 찾을 수 없습니다.")
            
        self.add_to_history(f"총 {len(rows)}건 처리 시작")
        self.add_to_history(f"파일 URL 컬럼: {', '.join(file_columns)}")
        
        for row in rows:
            for col in file_columns:
                raw_url = row[col]
                if not is_file_url(raw_url):
                    continue
                    
                file_url = normalize_url(raw_url)
                original_name = file_url.split('/')[-1]
                
                try:
                    response = requests.get(file_url)
                    response.raise_for_status()
                    
                    mime_type = mimetypes.guess_type(original_name)[0] or 'application/octet-stream'
                    storage_path = await upload_file_to_supabase(
                        response.content,
                        original_name,
                        mime_type
                    )
                    public_url = get_public_url(storage_path)
                    row[col] = public_url
                    self.add_to_history(f"업로드 완료: {original_name}", "success")
                    
                except Exception as e:
                    self.add_to_history(f"실패 ({file_url}): {str(e)}", "error")
                    
        with open(self.output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
            
        self.add_to_history(f"완료! 업데이트된 CSV 저장됨 → {os.path.basename(self.output_file)}", "success")
        
    def start_conversion(self):
        try:
            if not self.input_file or not self.output_file:
                QMessageBox.warning(self, "파일 선택 필요", "입력 파일과 출력 파일을 모두 선택해주세요.")
                return
                
            self.status_label.setText("변환 중...")
            self.status_label.setStyleSheet("color: #666;")
            QApplication.processEvents()
            
            asyncio.run(self.process_file())
            
            self.status_label.setText("✅ 변환 완료!")
            self.status_label.setStyleSheet("color: #28a745;")
            
            # 결과 파일이 있는 폴더 열기
            os.system(f"open {os.path.dirname(self.output_file)}")
            
        except Exception as e:
            self.status_label.setText(f"❌ 오류 발생: {str(e)}")
            self.status_label.setStyleSheet("color: #dc3545;")
            QMessageBox.critical(self, "오류", str(e))

def main():
    app = QApplication(sys.argv)
    window = LinkMappingWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()