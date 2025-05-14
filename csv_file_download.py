import csv
import os
import requests
from typing import List, Dict, Any
import asyncio
from datetime import datetime
from tqdm import tqdm
from urllib.parse import unquote

def is_bubble_url(value: str) -> bool:
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

def get_file_name(url: str) -> str:
    """
    URL에서 파일 경로를 추출하는 함수
    
    Args:
        url (str): 파일 URL
        
    Returns:
        str: 파일 경로
    """
    # URL 디코딩
    decoded_url = unquote(url)
    
    # bubble.io 도메인 이후의 경로를 추출
    path = decoded_url.split('.bubble.io/')[-1]
    if not path:
        return decoded_url.split('/')[-1]
    
    return path

async def download_file(url: str, save_dir: str) -> bool:
    """
    파일을 다운로드하는 함수
    
    Args:
        url (str): 다운로드할 파일의 URL
        save_dir (str): 파일을 저장할 디렉토리 경로
        
    Returns:
        bool: 다운로드 성공 여부
    """
    try:
        # URL 정규화
        normalized_url = normalize_url(url)
        file_path = get_file_name(normalized_url)
        save_path = os.path.join(save_dir, file_path)
        
        # 파일이 저장될 디렉토리 생성
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 이미 존재하는 파일인 경우 스킵
        if os.path.exists(save_path):
            print(f"⚠️ 파일이 이미 존재합니다: {file_path}")
            return False
        
        # 파일 다운로드
        response = requests.get(normalized_url, stream=True)
        response.raise_for_status()
        
        # 파일 저장
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"✅ 다운로드 완료: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 다운로드 실패 ({url}): {str(e)}")
        return False

async def process_csv(csv_path: str):
    """
    CSV 파일을 처리하는 메인 함수
    
    Args:
        csv_path (str): 처리할 CSV 파일 경로
    """
    if not os.path.exists(csv_path):
        raise Exception(f"CSV 파일을 찾을 수 없습니다: {csv_path}")
    
    # CSV 파일명 추출 (확장자 제외)
    csv_name = os.path.splitext(os.path.basename(csv_path))[0]
    
    # 저장 디렉토리 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_dir = f"{csv_name}_{timestamp}"
    os.makedirs(save_dir, exist_ok=True)
    
    # CSV 파일 읽기
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    
    if not rows:
        print("❌ CSV 파일이 비어있습니다.")
        return
    
    # bubble.io URL이 포함된 컬럼 찾기
    columns = rows[0].keys()
    file_columns = [
        col for col in columns 
        if any(is_bubble_url(row[col]) for row in rows)
    ]
    
    if not file_columns:
        print("❌ bubble.io URL을 포함한 컬럼을 찾을 수 없습니다.")
        return
    
    print(f"🔍 총 {len(rows)}건의 데이터 처리 시작")
    print(f"📁 저장 경로: {os.path.abspath(save_dir)}")
    print(f"🔍 처리할 컬럼: {', '.join(file_columns)}")
    
    # 전체 URL 수 계산
    total_urls = sum(1 for row in rows for col in file_columns if is_bubble_url(row[col]))
    success_count = 0
    
    # 진행 상황 표시를 위한 tqdm 초기화
    with tqdm(total=total_urls, desc="다운로드 진행률") as pbar:
        # 각 행의 URL 처리
        for row in rows:
            for col in file_columns:
                url = row[col]
                if not is_bubble_url(url):
                    continue
                
                if await download_file(url, save_dir):
                    success_count += 1
                pbar.update(1)
    
    print(f"\n🎉 작업 완료!")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {total_urls - success_count}개")
    print(f"📁 다운로드 경로: {os.path.abspath(save_dir)}")

def main():
    """
    메인 함수
    """
    # CSV 파일 경로 입력 받기
    csv_path = input("CSV 파일 경로를 입력하세요: ").strip()
    
    try:
        # 비동기 함수 실행
        asyncio.run(process_csv(csv_path))
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
