#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/utils/safety.py
생성일: 2025-04-03

안전한 종료 및 예외 처리를 담당하는 모듈입니다.
시그널 핸들링, 안전한 요청 등의 기능을 제공합니다.
"""

import signal
import logging
import time
import re
from typing import Callable, Optional, Any
import requests
from requests.exceptions import RequestException


# 로거 설정
logger = logging.getLogger(__name__)


def set_exit_handler(handler_func: Callable):
    """
    종료 핸들러 설정
    
    Args:
        handler_func (callable): 종료 시 호출할 핸들러 함수
    """
    def signal_handler(signum, frame):
        """
        시그널 핸들러
        
        Args:
            signum: 시그널 번호
            frame: 현재 스택 프레임
        """
        signal_name = signal.Signals(signum).name
        logger.info(f"시그널 {signal_name} ({signum}) 감지됨")
        
        # 종료 전 핸들러 함수 호출
        try:
            handler_func()
        except Exception as e:
            logger.error(f"종료 핸들러 오류: {e}")
        
        # 종료 메시지
        logger.info("안전하게 종료합니다...")
        
        # 프로세스 종료
        raise SystemExit(0)
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # 종료 시그널
    
    logger.debug("종료 핸들러가 설정되었습니다.")


def safe_request(method: str, url: str, **kwargs) -> Optional[requests.Response]:
    """
    안전한 HTTP 요청
    
    Args:
        method (str): HTTP 메서드 ('GET', 'POST' 등)
        url (str): 요청 URL
        **kwargs: requests 라이브러리에 전달할 추가 인자
    
    Returns:
        requests.Response: 응답 객체 (실패 시 None)
    """
    max_retries = kwargs.pop('max_retries', 3)
    retry_delay = kwargs.pop('retry_delay', 1)
    
    for retry in range(max_retries):
        try:
            # 요청 타임아웃 설정
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 30
            
            # 요청 실행
            response = requests.request(method, url, **kwargs)
            
            # 상태 코드 확인
            if response.status_code >= 400:
                logger.warning(f"HTTP 오류: {response.status_code} ({url})")
                if retry < max_retries - 1:
                    time.sleep(retry_delay * (retry + 1))
                    continue
                else:
                    return None
            
            return response
            
        except RequestException as e:
            logger.error(f"요청 오류 ({url}): {e}")
            if retry < max_retries - 1:
                time.sleep(retry_delay * (retry + 1))
            else:
                return None
        
        except Exception as e:
            logger.error(f"알 수 없는 요청 오류 ({url}): {e}")
            return None
    
    return None


def safe_regex(pattern: str, text: str, default: Any = None) -> Any:
    """
    안전한 정규식 적용
    
    Args:
        pattern (str): 정규식 패턴
        text (str): 검색할 텍스트
        default (any, optional): 실패 시 기본값. 기본값 None
    
    Returns:
        일치하는 문자열 또는 기본값
    """
    if not text:
        return default
    
    try:
        match = re.search(pattern, text)
        if match:
            return match.group(1) if match.groups() else match.group(0)
        else:
            return default
            
    except Exception as e:
        logger.error(f"정규식 오류 ({pattern}): {e}")
        return default


def safe_parse_int(text: str, default: int = 0) -> int:
    """
    안전한 정수 변환
    
    Args:
        text (str): 변환할 텍스트
        default (int, optional): 실패 시 기본값. 기본값 0
    
    Returns:
        int: 변환된 정수 또는 기본값
    """
    if not text:
        return default
    
    try:
        # 숫자만 추출
        num_text = re.sub(r'[^\d]', '', text)
        
        if not num_text:
            return default
        
        return int(num_text)
        
    except Exception as e:
        logger.error(f"정수 변환 오류 ({text}): {e}")
        return default


def safe_parse_float(text: str, default: float = 0.0) -> float:
    """
    안전한 실수 변환
    
    Args:
        text (str): 변환할 텍스트
        default (float, optional): 실패 시 기본값. 기본값 0.0
    
    Returns:
        float: 변환된 실수 또는 기본값
    """
    if not text:
        return default
    
    try:
        # 숫자와 소수점만 추출
        num_text = re.sub(r'[^\d.]', '', text)
        
        if not num_text:
            return default
        
        return float(num_text)
        
    except Exception as e:
        logger.error(f"실수 변환 오류 ({text}): {e}")
        return default