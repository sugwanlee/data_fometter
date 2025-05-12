import csv
import os
import uuid
import mimetypes
from datetime import datetime
import requests
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import List, Dict, Any, Optional
from formatter_config import BUCKET_CONFIGS  # formatter_config 설정 임포트
from urllib.parse import unquote  # URL 디코딩을 위해 추가

load_dotenv()

# 🔧 Supabase 설정
# Supabase 프로젝트 URL과 API 키를 설정합니다
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
PUBLIC_BUCKET = ['image', 'track/mp3', 'track/wav', 'business', 'other']  # 버킷 이름 목록

# 파일 형식별 업로드 경로 매핑
FILE_TYPE_MAPPING = {
    # 이미지 파일
    '.png': 'image',
    '.jpg': 'image',
    '.jfif': 'image',
    
    # 오디오 파일
    '.mp3': 'track/mp3',
    '.wav': 'track/wav',
    
    # 문서 파일
    '.pdf': 'business',
}

# 기본 업로드 경로 (매핑되지 않은 파일 형식용)
DEFAULT_UPLOAD_PATH = 'other'

# 입출력 CSV 파일 설정
INPUT_CSV = 'bubble_files.csv'  # 원본 bubble.io URL이 있는 CSV 파일
OUTPUT_CSV = 'updated_bubble_files.csv'  # 변환된 URL이 저장될 CSV 파일

# Supabase 클라이언트 초기화
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def is_file_url(value: str) -> bool:
    """
    주어진 값이 bubble.io 파일 URL인지 확인하는 함수
    
    Args:
        value (str): 확인할 URL 문자열
        
    Returns:
        bool: bubble.io URL이면 True, 아니면 False
    """
    return isinstance(value, str) and 'bubble.io' in value

def normalize_url(url: str) -> str:
    """
    URL을 정규화하는 함수
    - '//'로 시작하는 URL을 'https://'로 변환
    - URL 인코딩된 문자를 디코딩
    
    Args:
        url (str): 정규화할 URL
        
    Returns:
        str: 정규화된 URL
    """
    # URL 디코딩
    decoded_url = unquote(url)
    
    # '//'로 시작하는 경우 'https:'를 추가
    if decoded_url.startswith('//'):
        return f'https:{decoded_url}'
    # 'http://' 또는 'https://'로 시작하지 않는 경우 'https://'를 추가
    elif not decoded_url.startswith(('http://', 'https://')):
        return f'https://{decoded_url}'
    return decoded_url

def get_bucket_config(table_name: str, column_name: str) -> Dict[str, Any]:
    """
    테이블과 컬럼에 해당하는 버킷 설정을 반환합니다.
    
    Args:
        table_name (str): 테이블 이름
        column_name (str): 컬럼 이름
        
    Returns:
        Dict[str, Any]: 버킷 설정 정보
    """
    table_config = BUCKET_CONFIGS.get(table_name, {})
    return table_config.get(column_name, {})

def get_file_name(original_name: str, bucket_config: Dict[str, Any], row: Dict[str, Any]) -> str:
    """
    파일 이름을 생성합니다. filename_pattern이 있으면 사용하고, 없으면 기본 패턴을 사용합니다.
    
    Args:
        original_name (str): 원본 파일 이름
        bucket_config (Dict[str, Any]): 버킷 설정
        row (Dict[str, Any]): 현재 처리 중인 데이터 행
        
    Returns:
        str: 생성된 파일 이름
    """
    if 'filename_pattern' in bucket_config:
        try:
            return bucket_config['filename_pattern'](row)
        except:
            pass
    
    timestamp = int(datetime.now().timestamp() * 1000)
    unique_id = str(uuid.uuid4())
    sanitized_name = original_name.replace(' ', '_')
    return f"{timestamp}_{unique_id}_{sanitized_name}"

async def upload_file_to_supabase(file_content: bytes, original_name: str, mime_type: str, 
                                table_name: str, column_name: str, row: Dict[str, Any]) -> str:
    """
    파일을 Supabase 스토리지에 업로드하는 함수
    
    Args:
        file_content (bytes): 업로드할 파일의 바이너리 내용
        original_name (str): 원본 파일 이름
        mime_type (str): 파일의 MIME 타입
        table_name (str): 테이블 이름
        column_name (str): 컬럼 이름
        row (Dict[str, Any]): 현재 처리 중인 데이터 행
        
    Returns:
        str: Supabase에 업로드된 파일의 경로 (버킷 이름 포함)
    """
    bucket_config = get_bucket_config(table_name, column_name)
    if not bucket_config:
        raise Exception(f"버킷 설정을 찾을 수 없습니다: {table_name}.{column_name}")
    
    bucket_name = bucket_config['name']
    storage_path = bucket_config['path']
    
    try:
        # 첫 번째 시도: 원본 파일 이름으로 업로드
        file_name = original_name.split('/')[-1]
        upload_path = f"{storage_path}/{file_name}"
        
        try:
            # 기존 파일이 있다면 삭제
            try:
                supabase.storage.from_(bucket_name).remove([upload_path])
            except:
                pass  # 파일이 없어도 무시
            
            # 새로운 파일 업로드
            result = supabase.storage.from_(bucket_name).upload(
                upload_path,
                file_content,
                {"content-type": mime_type}
            )
            return f"{bucket_name}/{upload_path}"  # 버킷 이름과 경로 조합
        except Exception as e:
            if '400' in str(e):  # 400 에러 발생 시 filename_pattern으로 재시도
                file_name = get_file_name(original_name, bucket_config, row)
                upload_path = f"{storage_path}/{file_name}"
                
                # 기존 파일이 있다면 삭제
                try:
                    supabase.storage.from_(bucket_name).remove([upload_path])
                except:
                    pass  # 파일이 없어도 무시
                
                # 새로운 파일 업로드
                result = supabase.storage.from_(bucket_name).upload(
                    upload_path,
                    file_content,
                    {"content-type": mime_type}
                )
                return f"{bucket_name}/{upload_path}"  # 버킷 이름과 경로 조합
            raise e
            
    except Exception as e:
        raise Exception(f"Upload failed: {str(e)}")

def get_public_url(path: str) -> str:
    """
    Supabase 스토리지의 파일에 대한 공개 URL을 생성하는 함수
    
    Args:
        path (str): Supabase 스토리지 내 파일 경로 (버킷 이름 포함)
        
    Returns:
        str: 파일의 공개 접근 URL
    """
    # 경로에서 버킷 이름과 파일 경로 분리
    parts = path.split('/', 1)
    bucket = parts[0]
    file_path = parts[1] if len(parts) > 1 else ''
    
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_path}"

def find_table_for_column(column_name: str) -> Optional[str]:
    """
    주어진 컬럼이 어느 테이블에 속하는지 찾습니다.
    
    Args:
        column_name (str): 찾을 컬럼 이름
        
    Returns:
        Optional[str]: 테이블 이름. 찾지 못한 경우 None
    """
    for table_name, config in BUCKET_CONFIGS.items():
        if column_name in config:
            return table_name
    return None

async def process_csv():
    """
    CSV 파일을 처리하는 메인 함수
    1. CSV 파일 읽기
    2. bubble.io URL 찾기
    3. 각 URL의 파일을 다운로드하여 Supabase에 업로드
    4. 새로운 URL로 교체
    5. 결과를 새로운 CSV 파일로 저장
    """
    rows: List[Dict[str, Any]] = []
    
    # CSV 파일 읽기
    with open(INPUT_CSV, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    
    print(f"🔍 총 {len(rows)}건 처리 시작")
    
    if not rows:
        print("❌ CSV 파일이 비어있습니다.")
        return
    
    columns = rows[0].keys()
    
    # 테이블 이름 확인 (CSV 파일명 또는 사용자 입력 필요)
    table_name = input("테이블 이름을 입력하세요: ").lower()
    if table_name not in BUCKET_CONFIGS:
        print(f"❌ 지원하지 않는 테이블입니다: {table_name}")
        return
    
    # 처리할 컬럼 찾기
    valid_columns = BUCKET_CONFIGS[table_name].keys()
    file_columns = [col for col in columns if col in valid_columns]
    
    if not file_columns:
        print("❌ 처리할 컬럼을 찾을 수 없습니다.")
        return
    
    print(f"✅ 처리할 컬럼: {', '.join(file_columns)}")
    
    # 각 행의 URL 처리
    for row in rows:
        for col in file_columns:
            raw_url = row[col]
            if not is_file_url(raw_url):
                continue
            
            # URL 정규화 및 파일명 추출
            file_url = normalize_url(raw_url)
            original_name = file_url.split('/')[-1]
            
            try:
                # bubble.io에서 파일 다운로드
                response = requests.get(file_url)
                response.raise_for_status()
                
                # 파일의 MIME 타입 확인
                mime_type = mimetypes.guess_type(original_name)[0] or 'application/octet-stream'
                
                # Supabase에 파일 업로드
                storage_path = await upload_file_to_supabase(
                    response.content,
                    original_name,
                    mime_type,
                    table_name,
                    col,
                    row
                )
                # 새로운 공개 URL 생성
                public_url = get_public_url(storage_path)
                
                # 원본 URL을 새로운 URL로 교체
                row[col] = public_url
                print(f"📤 업로드 완료: {original_name}")
                
            except Exception as e:
                print(f"⚠️ 실패 ({file_url}): {str(e)}")
    
    # 변환된 데이터를 새로운 CSV 파일로 저장
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"🎉 완료! 업데이트된 CSV 저장됨 → {OUTPUT_CSV}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(process_csv())
