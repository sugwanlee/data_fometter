# 데이터 포맷터 & 링크 매핑 도구

이 프로젝트는 데이터 포맷팅과 파일 URL 매핑을 위한 두 가지 도구를 제공합니다.

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
- Excel (.xlsx, .xls)

## 2. 링크 매핑 도구 (Link Mapping)

### 기능
- Bubble.io URL을 Supabase 스토리지 URL로 변환
- 파일 자동 다운로드 및 업로드
- 파일 타입별 자동 분류

### 사용 방법
1. GUI 실행:
```bash
python link_mapping_gui.py
```

2. 입력/출력 CSV 파일 선택:
   - '입력 파일 선택' 버튼으로 Bubble.io URL이 포함된 CSV 파일 선택
   - '출력 파일 선택' 버튼으로 결과를 저장할 CSV 파일 선택

3. 변환 시작:
   - '변환 시작' 버튼 클릭
   - 변환 진행 상황이 실시간으로 표시됨

### 파일 타입별 저장 경로
- 이미지 파일 (.png, .jpg, .jfif) → image/
- 오디오 파일 (.mp3) → track/mp3/
- 오디오 파일 (.wav) → track/wav/
- 문서 파일 (.pdf) → business/

### 특수 컬럼 처리
- imgprofile 컬럼 → profile-images/
- contractfile 컬럼 → contract/

## 환경 설정

### 필요한 Python 패키지
```
pandas
PyQt5
requests
supabase
```

### Supabase 설정
`.env` 파일에서 다음 설정을 변경하세요:
```python
SUPABASE_URL = 'your-project-url'
SUPABASE_KEY = 'your-service-role-key'
```

## 주의사항
1. 대용량 파일 처리 시 메모리 사용량에 주의
2. Supabase 스토리지 용량 제한 확인
3. 네트워크 연결 상태 확인
