import csv
import os
import uuid
import mimetypes
from datetime import datetime
import requests
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import List, Dict, Any

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
    '//'로 시작하는 URL을 'https://'로 변환
    
    Args:
        url (str): 정규화할 URL
        
    Returns:
        str: 정규화된 URL
    """
    return f'https:{url}' if url.startswith('//') else url

def get_upload_path(file_name: str, column_name: str = None) -> str:
    """
    파일 이름에 따라 적절한 업로드 경로를 반환하는 함수
    
    Args:
        file_name (str): 파일 이름 또는 URL
        column_name (str, optional): CSV 컬럼 이름
        
    Returns:
        str: 업로드 경로
    """
    # 특수 컬럼별 경로 매핑
    if column_name == 'imgprofile':
        return 'profile-images'
    elif column_name == 'contractfile':
        return 'contract'
    
    # URL에서 파일 이름 추출
    if '?' in file_name:
        file_name = file_name.split('?')[0]  # URL 파라미터 제거
    
    # 파일 확장자 추출
    _, ext = os.path.splitext(file_name.lower())
    
    # 확장자가 없는 경우 MIME 타입으로 확인
    if not ext:
        # URL에서 파일 이름만 추출
        file_name = file_name.split('/')[-1]
        _, ext = os.path.splitext(file_name.lower())
    
    # 매핑된 경로 반환 또는 기본 경로 사용
    return FILE_TYPE_MAPPING.get(ext, DEFAULT_UPLOAD_PATH)

async def upload_file_to_supabase(file_content: bytes, original_name: str, mime_type: str, column_name: str = None) -> str:
    """
    파일을 Supabase 스토리지에 업로드하는 함수
    
    Args:
        file_content (bytes): 업로드할 파일의 바이너리 내용
        original_name (str): 원본 파일 이름
        mime_type (str): 파일의 MIME 타입
        column_name (str, optional): CSV 컬럼 이름
        
    Returns:
        str: Supabase에 업로드된 파일의 경로
        
    Raises:
        Exception: 업로드 실패 시 예외 발생
    """
    # 고유한 파일명 생성 (타임스탬프 + UUID + 원본파일명)
    timestamp = int(datetime.now().timestamp() * 1000)
    unique_id = str(uuid.uuid4())
    sanitized_name = original_name.replace(' ', '_')
    new_file_name = f"{timestamp}_{unique_id}_{sanitized_name}"
    
    # 파일 형식에 따른 업로드 경로 결정
    upload_dir = get_upload_path(original_name, column_name)
    upload_path = f"{upload_dir}/{new_file_name}"

    try:
        # Supabase 스토리지에 파일 업로드
        bucket = upload_dir.split('/')[0]  # 첫 번째 디렉토리를 버킷 이름으로 사용
        result = supabase.storage.from_(bucket).upload(
            upload_path,
            file_content,
            {"content-type": mime_type}
        )
        return upload_path
    except Exception as e:
        raise Exception(f"Upload failed: {str(e)}")

def get_public_url(path: str) -> str:
    """
    Supabase 스토리지의 파일에 대한 공개 URL을 생성하는 함수
    
    Args:
        path (str): Supabase 스토리지 내 파일 경로
        
    Returns:
        str: 파일의 공개 접근 URL
    """
    # 경로에서 버킷 이름 추출 (첫 번째 디렉토리)
    bucket = path.split('/')[0]
    # 버킷 이름을 제외한 나머지 경로
    file_path = '/'.join(path.split('/')[1:])
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_path}"

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
    
    # bubble.io URL이 포함된 컬럼 찾기
    file_columns = [
        col for col in columns 
        if any(is_file_url(row[col]) for row in rows)
    ]
    
    if not file_columns:
        print("❌ 파일 URL을 포함한 컬럼을 찾을 수 없습니다.")
        return
    
    print(f"✅ 파일 URL 컬럼: {', '.join(file_columns)}")
    
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
                    col  # 컬럼 이름 전달
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
