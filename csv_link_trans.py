import csv
import os
from datetime import datetime
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

def convert_to_s3_url(bubble_url: str) -> str:
    """
    bubble.io URL을 S3 URL로 변환하는 함수
    
    Args:
        bubble_url (str): 변환할 bubble.io URL
        
    Returns:
        str: 변환된 S3 URL
    """
    # URL 디코딩
    decoded_url = unquote(bubble_url)
    
    # bubble.io 도메인 이후의 경로 추출
    path = decoded_url.split('.bubble.io/')[-1] if '.bubble.io/' in decoded_url else decoded_url.split('bubble.io/')[-1]
    
    # S3 URL 생성
    s3_url = f"https://plpl-file-from-bubble.s3.ap-northeast-2.amazonaws.com/{path}"
    
    return s3_url

def process_csv(input_csv_path: str):
    """
    CSV 파일을 처리하는 메인 함수
    
    Args:
        input_csv_path (str): 처리할 CSV 파일 경로
    """
    if not os.path.exists(input_csv_path):
        raise Exception(f"CSV 파일을 찾을 수 없습니다: {input_csv_path}")
    
    # CSV 파일명과 확장자 분리
    csv_name, csv_ext = os.path.splitext(os.path.basename(input_csv_path))
    
    # 출력 파일명 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_csv_path = f"{csv_name}_converted_{timestamp}{csv_ext}"
    
    # CSV 파일 읽기
    rows = []
    with open(input_csv_path, 'r', encoding='utf-8') as file:
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
    print(f"🔍 처리할 컬럼: {', '.join(file_columns)}")
    
    # URL 변환
    converted_count = 0
    for row in rows:
        for col in file_columns:
            if is_bubble_url(row[col]):
                row[col] = convert_to_s3_url(row[col])
                converted_count += 1
    
    # 변환된 데이터를 새 CSV 파일로 저장
    with open(output_csv_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n🎉 작업 완료!")
    print(f"✅ 변환된 URL 수: {converted_count}개")
    print(f"📁 저장된 파일: {output_csv_path}")

def main():
    """
    메인 함수
    """
    # CSV 파일 경로 입력 받기
    csv_path = input("CSV 파일 경로를 입력하세요: ").strip()
    
    try:
        process_csv(csv_path)
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
