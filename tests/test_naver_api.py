#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from dotenv import load_dotenv
import requests
from urllib.parse import quote

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)

def test_naver_api():
    """
    네이버 검색 API 테스트
    """
    # 환경 변수에서 API 키 로드
    client_id = os.environ.get('NAVER_CLIENT_ID')
    client_secret = os.environ.get('NAVER_CLIENT_SECRET')

    # API 키 유효성 확인
    if not client_id or not client_secret:
        logger.error("네이버 API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return False

    logger.info("1. API 키 확인 ✓")

    # API 요청 헤더 설정
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "User-Agent": "NaverMediCollect/1.0"
    }

    # 테스트할 키워드들
    test_keywords = ["타이레놀", "소화제", "혈압약", "항생제"]

    # API 엔드포인트
    api_url = "https://openapi.naver.com/v1/search/encyc.json"

    for keyword in test_keywords:
        try:
            # 키워드 인코딩
            encoded_keyword = quote(keyword)
            
            # API 요청 파라미터
            params = {
                "query": encoded_keyword,
                "display": 10,
                "start": 1
            }

            # API 요청
            response = requests.get(
                api_url, 
                headers=headers, 
                params=params, 
                timeout=10
            )

            # 응답 상태 코드 확인
            if response.status_code == 200:
                result = response.json()
                
                logger.info(f"2. '{keyword}' 검색 결과: {len(result.get('items', []))}건")
                
                # 각 항목 상세 정보 출력
                for item in result.get('items', [])[:3]:  # 첫 3개 항목만 출력
                    logger.info(f"   - 제목: {item.get('title')}")
                    logger.info(f"   - 링크: {item.get('link')}")
            else:
                logger.error(f"API 요청 실패 ({keyword}): HTTP {response.status_code}")
                logger.error(f"응답 내용: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 오류 ({keyword}): {e}")
            return False

    logger.info("3. 모든 테스트 키워드 검색 성공 ✓")
    return True

def main():
    try:
        result = test_naver_api()
        sys.exit(0 if result else 1)
    except Exception as e:
        logger.exception("예상치 못한 오류 발생")
        sys.exit(1)

if __name__ == "__main__":
    main()