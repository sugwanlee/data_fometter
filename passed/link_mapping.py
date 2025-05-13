# import csv
# import os
# import uuid
# import mimetypes
# from datetime import datetime
# import requests
# from dotenv import load_dotenv
# from supabase import create_client, Client
# from typing import List, Dict, Any, Optional
# from formatter_config import BUCKET_CONFIGS  # formatter_config 설정 임포트
# from urllib.parse import unquote  # URL 디코딩을 위해 추가

# load_dotenv()

# # 🔧 Supabase 설정
# # Supabase 프로젝트 URL과 API 키를 설정합니다
# SUPABASE_URL = os.getenv('SUPABASE_URL')
# SUPABASE_KEY = os.getenv('SUPABASE_KEY')
# PUBLIC_BUCKET = ['image', 'track/mp3', 'track/wav', 'business', 'other']  # 버킷 이름 목록

# # 파일 형식별 업로드 경로 매핑
# FILE_TYPE_MAPPING = {
#     # 이미지 파일
#     '.png': 'image',
#     '.jpg': 'image',
#     '.jfif': 'image',
    
#     # 오디오 파일
#     '.mp3': 'track/mp3',
#     '.wav': 'track/wav',
    
#     # 문서 파일
#     '.pdf': 'business',
# }

# # 기본 업로드 경로 (매핑되지 않은 파일 형식용)
# DEFAULT_UPLOAD_PATH = 'other'

# # 입출력 CSV 파일 설정
# INPUT_CSV = 'bubble_files.csv'  # 원본 bubble.io URL이 있는 CSV 파일
# OUTPUT_CSV = 'updated_bubble_files.csv'  # 변환된 URL이 저장될 CSV 파일

# # Supabase 클라이언트 초기화
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# # 파일 카운터를 저장할 전역 딕셔너리
# file_counters = {}

# def get_next_file_number(table_name: str, column_name: str) -> int:
#     """
#     테이블과 컬럼에 대한 다음 파일 번호를 반환합니다.
    
#     Args:
#         table_name (str): 테이블 이름
#         column_name (str): 컬럼 이름
        
#     Returns:
#         int: 다음 파일 번호
#     """
#     key = f"{table_name}_{column_name}"
#     if key not in file_counters:
#         file_counters[key] = 0
#     file_counters[key] += 1
#     return file_counters[key]

# def get_file_name(original_name: str, bucket_config: Dict[str, Any], row: Dict[str, Any], 
#                   table_name: str = None, column_name: str = None) -> str:
#     """
#     파일 이름을 생성합니다. filename_pattern이 있으면 사용하고, 
#     없으면 테이블명_컬럼명_순번.확장자 형식으로 생성합니다.
    
#     Args:
#         original_name (str): 원본 파일 이름
#         bucket_config (Dict[str, Any]): 버킷 설정
#         row (Dict[str, Any]): 현재 처리 중인 데이터 행
#         table_name (str, optional): 테이블 이름
#         column_name (str, optional): 컬럼 이름
        
#     Returns:
#         str: 생성된 파일 이름
#     """
#     # filename_pattern이 있으면 사용
#     if 'filename_pattern' in bucket_config:
#         try:
#             return bucket_config['filename_pattern'](row)
#         except:
#             pass
    
#     # filename_pattern이 없거나 실패한 경우
#     # 원본 파일의 확장자 추출
#     _, ext = os.path.splitext(original_name.lower())
#     if not ext and '?' in original_name:  # URL에 쿼리 파라미터가 있는 경우
#         ext = os.path.splitext(original_name.split('?')[0].lower())[1]
    
#     if not ext:  # 확장자가 없는 경우 MIME 타입으로 확장자 추정
#         mime_type = mimetypes.guess_type(original_name)[0]
#         if mime_type:
#             ext = mimetypes.guess_extension(mime_type) or '.bin'
#         else:
#             ext = '.bin'
    
#     # 테이블명과 컬럼명이 제공된 경우 사용
#     if table_name and column_name:
#         file_number = get_next_file_number(table_name, column_name)
#         return f"{table_name}_{column_name}_{file_number}{ext}"
    
#     # 테이블명과 컬럼명이 없는 경우 기본 형식 사용
#     timestamp = int(datetime.now().timestamp() * 1000)
#     unique_id = str(uuid.uuid4())
#     return f"{timestamp}_{unique_id}{ext}"

# async def upload_file_to_supabase(file_content: bytes, original_name: str, mime_type: str, 
#                                 table_name: str, column_name: str, row: Dict[str, Any]) -> str:
#     """
#     파일을 Supabase 스토리지에 업로드하는 함수
    
#     Args:
#         file_content (bytes): 업로드할 파일의 바이너리 내용
#         original_name (str): 원본 파일 이름
#         mime_type (str): 파일의 MIME 타입
#         table_name (str): 테이블 이름
#         column_name (str): 컬럼 이름
#         row (Dict[str, Any]): 현재 처리 중인 데이터 행
        
#     Returns:
#         str: Supabase에 업로드된 파일의 경로 (버킷 이름 포함)
#     """
#     bucket_config = get_bucket_config(table_name, column_name)
#     if not bucket_config:
#         raise Exception(f"버킷 설정을 찾을 수 없습니다: {table_name}.{column_name}")
    
#     bucket_name = bucket_config['name']
#     storage_path = bucket_config['path']
    
#     try:
#         # 첫 번째 시도: 원본 파일 이름으로 업로드
#         file_name = original_name.split('/')[-1]
#         upload_path = f"{storage_path}/{file_name}"
        
#         try:
#             # 기존 파일이 있다면 삭제
#             try:
#                 supabase.storage.from_(bucket_name).remove([upload_path])
#             except:
#                 pass  # 파일이 없어도 무시
            
#             # 새로운 파일 업로드
#             result = supabase.storage.from_(bucket_name).upload(
#                 upload_path,
#                 file_content,
#                 {"content-type": mime_type}
#             )
#             return f"{bucket_name}/{upload_path}"  # 버킷 이름과 경로 조합
#         except Exception as e:
#             if '400' in str(e):  # 400 에러 발생 시 filename_pattern으로 재시도
#                 file_name = get_file_name(original_name, bucket_config, row, table_name, column_name)
#                 upload_path = f"{storage_path}/{file_name}"
                
#                 # 기존 파일이 있다면 삭제
#                 try:
#                     supabase.storage.from_(bucket_name).remove([upload_path])
#                 except:
#                     pass  # 파일이 없어도 무시
                
#                 # 새로운 파일 업로드
#                 result = supabase.storage.from_(bucket_name).upload(
#                     upload_path,
#                     file_content,
#                     {"content-type": mime_type}
#                 )
#                 return f"{bucket_name}/{upload_path}"  # 버킷 이름과 경로 조합
#             raise e
            
#     except Exception as e:
#         raise Exception(f"Upload failed: {str(e)}")

# def get_public_url(path: str) -> str:
#     """
#     Supabase 스토리지의 파일에 대한 공개 URL을 생성하는 함수
    
#     Args:
#         path (str): Supabase 스토리지 내 파일 경로 (버킷 이름 포함)
        
#     Returns:
#         str: 파일의 공개 접근 URL
#     """
#     # 경로에서 버킷 이름과 파일 경로 분리
#     parts = path.split('/', 1)
#     bucket = parts[0]
#     file_path = parts[1] if len(parts) > 1 else ''
    
#     return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_path}"

# def find_table_for_column(column_name: str) -> Optional[str]:
#     """
#     주어진 컬럼이 어느 테이블에 속하는지 찾습니다.
    
#     Args:
#         column_name (str): 찾을 컬럼 이름
        
#     Returns:
#         Optional[str]: 테이블 이름. 찾지 못한 경우 None
#     """
#     for table_name, config in BUCKET_CONFIGS.items():
#         if column_name in config:
#             return table_name
#     return None

# def is_file_url(value: str) -> bool:
#     """
#     주어진 값이 bubble.io 파일 URL인지 확인하는 함수
    
#     Args:
#         value (str): 확인할 URL 문자열
        
#     Returns:
#         bool: bubble.io URL이면 True, 아니면 False
#     """
#     return isinstance(value, str) and 'bubble.io' in value

# def normalize_url(url: str) -> str:
#     """
#     URL을 정규화하는 함수
#     - '//'로 시작하는 URL을 'https://'로 변환
#     - URL 인코딩된 문자를 디코딩
    
#     Args:
#         url (str): 정규화할 URL
        
#     Returns:
#         str: 정규화된 URL
#     """
#     # URL 디코딩
#     decoded_url = unquote(url)
    
#     # '//'로 시작하는 경우 'https:'를 추가
#     if decoded_url.startswith('//'):
#         return f'https:{decoded_url}'
#     # 'http://' 또는 'https://'로 시작하지 않는 경우 'https://'를 추가
#     elif not decoded_url.startswith(('http://', 'https://')):
#         return f'https://{decoded_url}'
#     return decoded_url

# async def process_csv():
#     """
#     CSV 파일을 처리하는 메인 함수
#     """
#     if not os.path.exists(INPUT_CSV):
#         raise Exception(f"입력 파일을 찾을 수 없습니다: {INPUT_CSV}")
            
#     # CSV 파일 읽기
#     rows = []
#     with open(INPUT_CSV, 'r', encoding='utf-8') as file:
#         reader = csv.DictReader(file)
#         rows = list(reader)
            
#     if not rows:
#         print("❌ CSV 파일이 비어있습니다.")
#         return
            
#     print(f"🔍 총 {len(rows)}건 처리 시작")
    
#     # 처리할 컬럼 찾기
#     columns = rows[0].keys()
#     file_columns = [
#         col for col in columns 
#         if any(is_file_url(row[col]) for row in rows)
#     ]
    
#     if not file_columns:
#         print("❌ bubble.io URL을 포함한 컬럼을 찾을 수 없습니다.")
#         return
    
#     print(f"✅ 파일 URL 컬럼: {', '.join(file_columns)}")
    
#     # 각 행의 URL 처리
#     for row in rows:
#         for col in file_columns:
#             raw_url = row[col]
#             if not is_file_url(raw_url):
#                 continue
            
#             # 테이블 찾기
#             table_name = None
#             for t_name, t_config in BUCKET_CONFIGS.items():
#                 if col in t_config:
#                     table_name = t_name
#                     break
            
#             if not table_name:
#                 print(f"⚠️ 컬럼 '{col}'에 대한 테이블을 찾을 수 없습니다.")
#                 continue
                
#             file_url = normalize_url(raw_url)
#             original_name = file_url.split('/')[-1]
            
#             try:
#                 response = requests.get(file_url)
#                 response.raise_for_status()
                
#                 mime_type = mimetypes.guess_type(original_name)[0] or 'application/octet-stream'
#                 storage_path = await upload_file_to_supabase(
#                     response.content,
#                     original_name,
#                     mime_type,
#                     table_name,
#                     col,
#                     row
#                 )
#                 public_url = get_public_url(storage_path)
#                 row[col] = public_url
#                 print(f"📤 업로드 완료: {original_name}")
                
#             except Exception as e:
#                 print(f"⚠️ 실패 ({file_url}): {str(e)}")
                    
#     # 변환된 데이터를 새로운 CSV 파일로 저장
#     with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as file:
#         writer = csv.DictWriter(file, fieldnames=columns)
#         writer.writeheader()
#         writer.writerows(rows)
            
#     print(f"🎉 완료! 업데이트된 CSV 저장됨 → {OUTPUT_CSV}")

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(process_csv())
