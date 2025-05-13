# 데이터 포맷터 & 링크 매핑 도구

## 1. 매핑 GUI 사용법 (Mapping GUI)

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

## 2. 데이터 포맷터 (Data Formatter)

### 기능
- CSV파일의 데이터를 자동으로 포맷팅
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

### 포맷터 설정 가이드 (formatter_config.py)

#### 1. 기본값 설정
```python
DEFAULT_VALUE_MAPPING = {
    'label': '0000000000000x000000000000000001',  # label_formatted 필드의 기본값
    'ownershiplabel': '0000000000000x000000000000000001',  # ownershiplabel_formatted의 기본값
    # ... 다른 기본값들
}
```

#### 2. 테이블별 설정
```python
TABLE_CONFIGS = {
    '테이블명': {
        'required_columns': ['원본 컬럼1', '원본 컬럼2'],  # 반드시 있어야 하는 컬럼들
        'uuid_columns': {
            '변환될_컬럼명': '원본_컬럼명'  # UUID 형식으로 변환될 컬럼 매핑
        },
        'default_values': {
            '컬럼명': '기본값'  # 값이 없을 때 사용할 기본값
        }
    }
}
```

#### 설정 예시
1. 뮤지션 테이블 설정:
```python
'musician': {
    'required_columns': ['unique id', 'label'],
    'uuid_columns': {
        'unique_id': 'unique id',
        'label_formatted': 'label'
    },
    'default_values': {
        'label': DEFAULT_VALUE_MAPPING['label']
    }
}
```

2. 트랙 테이블 설정:
```python
'track': {
    'required_columns': ['unique id', 'ownershipshared'],
    'uuid_columns': {
        'unique_id': 'unique id',
        'ownership_shared': 'ownershipshared'
    },
    'default_values': {
        'ownershipshared': DEFAULT_VALUE_MAPPING['ownershipshared']
    }
}
```

#### 설정 수정 방법
1. 새로운 테이블 추가:
   - TABLE_CONFIGS에 새로운 테이블 설정 추가
   - 필수 컬럼, 기본값 정의

2. 기존 테이블 수정:
   - required_columns: 필수 컬럼 추가/제거
   - uuid_columns: UUID 변환 규칙 수정
   - default_values: 기본값 수정

3. 기본값 수정:
   - DEFAULT_VALUE_MAPPING에서 원하는 값 수정
   - 여러 테이블에서 공유되는 기본값 관리