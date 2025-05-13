# 필요한 도구들을 가져옵니다
import pandas as pd  # 엑셀 파일을 쉽게 다룰 수 있게 해주는 도구
import hashlib  # 텍스트를 해시로 바꿀 때 사용하는 도구
from datetime import datetime  # 날짜와 시간을 다룰 때 사용하는 도구
import re  # 텍스트 패턴을 찾을 때 사용하는 도구
import os  # 파일 경로를 다룰 때 사용하는 도구
from formatter_config import TABLE_CONFIGS

def generate_uuid_from_text(text):
    """
    텍스트를 UUID로 바꾸는 함수
    쉼표로 구분된 여러 값이 있는 경우 각각 UUID로 변환
    예시: 
    - "안녕하세요" -> "550e8400-e29b-41d4-a716-446655440000"
    - "안녕,반갑" -> "550e8400-e29b-41d4-a716-446655440000,123e4567-e89b-12d3-a456-426614174000"
    """
    # 쉼표로 구분된 값들을 분리
    values = [v.strip() for v in str(text).split(',')]
    
    # 각 값을 UUID로 변환
    uuids = []
    for value in values:
        if value:  # 빈 문자열이 아닌 경우에만 처리
            # 텍스트를 SHA-1 해시로 바꿉니다
            hash_obj = hashlib.sha1(value.encode())
            hex_str = hash_obj.hexdigest()
            
            # 해시를 UUID 형식으로 바꿉니다
            uuid_str = f"{hex_str[:8]}-{hex_str[8:12]}-5{hex_str[13:16]}-{hex(0x80 | (int(hex_str[16:18], 16) & 0x3f))[2:]}{hex_str[18:20]}-{hex_str[20:32]}"
            uuids.append(uuid_str)
    
    # 쉼표로 구분된 UUID 문자열 반환
    return ', '.join(uuids)

def parse_custom_date(input_str):
    """
    날짜 문자열을 ISO 형식으로 바꾸는 함수 (KST → UTC)
    예시: "Aug 16, 2023 6:02 pm" -> "2023-08-16 09:02:00+00"
    """
    # 입력이 비어있으면 None 반환
    if not input_str or str(input_str).strip() == "":
        return None
    
    try:
        # pandas로 일반적인 날짜 형식 시도 (KST로 가정)
        kst_time = pd.to_datetime(input_str)
        return kst_time.strftime('%Y-%m-%d %H:%M:%S+00')  # isoformat() 대신 strftime() 사용
    except:
        pass
    
    # 특별한 형식의 날짜를 찾습니다
    regex = r"^([A-Za-z]{3,}) (\d{1,2}), (\d{4}) (\d{1,2}):(\d{2}) (am|pm)$"
    match = re.match(regex, str(input_str).strip(), re.IGNORECASE)
    if not match:
        return None
    
    # 날짜의 각 부분을 분리합니다
    month_str, day, year, hour_str, minute, ampm = match.groups()
    
    # 월 이름을 숫자로 바꿉니다
    month_map = {
        'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
        'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
    }
    
    month = month_map[month_str[:3]]
    hour = int(hour_str)
    
    # AM/PM을 24시간 형식으로 바꿉니다
    if ampm.lower() == 'pm' and hour < 12:
        hour += 12
    elif ampm.lower() == 'am' and hour == 12:
        hour = 0
    
    try:
        date = datetime(int(year), month + 1, int(day), hour, int(minute))
        return date.strftime('%Y-%m-%d %H:%M:%S+00')  # isoformat() 대신 strftime() 사용
    except:
        return None

def format_sheet(df, table_type):
    """
    데이터프레임을 포맷팅하는 함수
    
    Args:
        df (pandas.DataFrame): 처리할 데이터프레임
        table_type (str): 테이블 타입
    
    Returns:
        pandas.DataFrame: 포맷팅된 데이터프레임
    """
    # 테이블 타입 확인
    if table_type not in TABLE_CONFIGS:
        raise ValueError(f"❌ 지원하지 않는 테이블 타입입니다: {table_type}")
    
    config = TABLE_CONFIGS[table_type]
    
    # 모든 컬럼 이름을 소문자로 바꾸고 앞뒤 공백을 제거합니다
    df.columns = [str(col).lower().strip() for col in df.columns]
    
    # 필수 컬럼 확인
    for col in config['required_columns']:
        if col not in df.columns:
            raise ValueError(f"❌ '{col}' 컬럼이 없습니다")
    
    # 1. 먼저 빈 값이 있는 컬럼들을 채웁니다
    for new_col, old_col in config['uuid_columns'].items():
        # 원본 컬럼의 빈 값 채우기
        if old_col in config.get('default_values', {}):
            df[old_col] = df[old_col].apply(
                lambda x: config['default_values'][old_col] if pd.isna(x) or str(x).strip() == "" else x
            )
    
    # 2. 그 다음 변환된 컬럼들을 생성합니다
    for new_col, old_col in config['uuid_columns'].items():
        df[new_col] = df[old_col].apply(generate_uuid_from_text)
    
    # 날짜 컬럼 매핑 정의
    date_columns = {
        'creation date': 'created_date',
        'modified date': 'modified_date',
        'dateofbirth': 'date_of_birth',
        'joinedat': 'joined_at',
        'createdat': 'created_at',
        # 'leftat': 'left_at', 안쓰는 컬럼
        'cidexpiredat': 'cid_expired_at',
        'cidpublishedat': 'cid_published_at',
        'publishedat': 'published_at',
        'registeredat': 'registered_at',
        '발매일' : 'release_date',
        'profit date' : 'profit_date',
        'profitdate' : 'profit_date',
        'payoutdate' : 'payout_date',
        'requestdate' : 'request_date',
        'registeredat' : 'registered_at',
        'contractdate' : 'contract_date',
        'testperiod' : 'test_period',
        'dateupload' : 'date_upload',
        'dateuploadplpl' : 'date_upload_plpl',
    }

    # 날짜 컬럼 처리
    for old_col, new_col in date_columns.items():
        if old_col in df.columns:
            df[new_col] = df[old_col].apply(parse_custom_date)
    
    # Boolean 변환 처리
    for col in df.columns:
        df[col] = df[col].apply(lambda x: True if str(x).strip() == '네' else (False if str(x).strip() == '아니오' else x))
    
    return df

def format_data(file_path, output_dir=None):
    """
    엑셀 파일의 모든 시트를 포맷팅하는 함수
    
    Args:
        file_path (str): 처리할 파일의 경로
        output_dir (str, optional): 출력 파일을 저장할 디렉토리 경로
    
    Returns:
        str: 포맷팅된 파일의 경로
    """
    # 파일 확장자 확인
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # 출력 디렉토리 설정
    if output_dir is None:
        output_dir = os.path.dirname(file_path)
    else:
        # 출력 디렉토리가 없으면 생성
        os.makedirs(output_dir, exist_ok=True)
    
    if file_extension == '.csv':
        # CSV 파일명에서 테이블 타입 추출
        file_name = os.path.basename(file_path).lower()
        table_type = None
        
        # 파일명에 테이블 타입이 포함되어 있는지 확인
        for type_name in TABLE_CONFIGS.keys():
            if type_name in file_name:
                table_type = type_name
                break
        
        if table_type is None:
            raise ValueError("❌ 파일명에서 테이블 타입을 찾을 수 없습니다.")
        
        # CSV 파일 처리
        df = pd.read_csv(file_path)
        formatted_df = format_sheet(df, table_type)
        
        # 결과 저장
        base_name = os.path.splitext(os.path.basename(file_path))[0] + '_formatted'
        output_path = os.path.join(output_dir, base_name + file_extension)
        
        # 파일이 이미 존재하면 번호를 붙입니다
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}_{counter}{file_extension}")
            counter += 1
        
        formatted_df.to_csv(output_path, index=False)
        print(f"✅ {table_type} 테이블 처리 완료")
    else:
        # Excel 파일은 모든 시트를 처리
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        # 결과를 저장할 ExcelWriter 객체 생성
        base_name = os.path.splitext(os.path.basename(file_path))[0] + '_formatted'
        output_path = os.path.join(output_dir, base_name + file_extension)
        
        # 파일이 이미 존재하면 번호를 붙입니다
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}_{counter}{file_extension}")
            counter += 1
        
        with pd.ExcelWriter(output_path) as writer:
            for sheet_name in sheet_names:
                try:
                    # 시트 이름을 테이블 타입으로 사용
                    table_type = sheet_name.lower()
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    formatted_df = format_sheet(df, table_type)
                    formatted_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"✅ {sheet_name} 시트 처리 완료")
                except Exception as e:
                    print(f"❌ {sheet_name} 시트 처리 실패: {str(e)}")
    
    return output_path

if __name__ == "__main__":
    # 파일 경로 입력 받기
    file_path = input("파일 경로를 입력하세요: ")
    
    try:
        output_path = format_data(file_path)
        print(f"\n변환 완료! 결과가 {output_path}에 저장되었습니다.")
    except Exception as e:
        print(f"오류 발생: {str(e)}") 