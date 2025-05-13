# 데이터 포맷터 & 링크 매핑 도구

## 매핑 GUI 사용법 (Mapping GUI)

### 기능
- CSV 파일에서 bubble.io URL을 찾아 파일 다운로드
- bubble.io URL을 S3 URL로 변환

### 사용 방법
1. GUI 실행:
```bash
python mapping_gui.py
```

2. CSV 파일 선택:
   - '파일 선택' 버튼을 클릭하여 bubble.io URL이 포함된 CSV 파일 선택

3. 작업 선택:
   - '파일 다운로드': bubble.io URL에서 파일을 다운로드
   - '링크 변환': bubble.io URL을 S3 URL로 변환

4. 진행 상황:
   - 터미널 창에서 진행 상황 확인 가능
   - 작업 완료 시 알림 표시
---

## 1. 데이터 포맷터 (Data Formatter)

### 기능
- CSV/Excel 파일의 데이터를 자동으로 포맷팅
- UUID 생성 및 변환
- 날짜 형식 표준화
- Boolean 값 변환 ('네'/'아니오' → True/False)

### 사용 방법
1. GUI 실행:
```bash
python data_formatter_gui.py
```

2. 파일 선택:
   - 드래그 앤 드롭으로 파일 추가
   - 또는 '파일 선택하기' 버튼 클릭

3. 출력 폴더 선택 (선택사항):
   - '출력 폴더 선택하기' 버튼으로 지정
   - 지정하지 않으면 입력 파일과 같은 위치에 저장

### 지원하는 파일 형식
- CSV (.csv)

```