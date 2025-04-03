#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - conf/settings.py
생성일: 2025-04-03

프로젝트 설정 및 상수를 관리하는 모듈입니다.
환경 변수, 전역 설정, 기본값 등을 제공합니다.
"""

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv


# .env 파일 로드
load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)


# 전역 설정
SETTINGS = {
    # API 설정
    'API': {
        'NAVER_CLIENT_ID': os.environ.get('NAVER_CLIENT_ID'),
        'NAVER_CLIENT_SECRET': os.environ.get('NAVER_CLIENT_SECRET'),
        'API_URL': 'https://openapi.naver.com/v1/search/encyc.json',
        'REQUEST_DELAY': 0.2,  # 초당 최대 5회 요청
        'MAX_RETRIES': 3,
        'RETRY_DELAY': 1,
        'TIMEOUT': 30,
        'USER_AGENT': 'NaverMediCollect/1.0'
    },
    
    # 데이터베이스 설정
    'DATABASE': {
        'TYPE': os.environ.get('DB_TYPE', 'mysql'),
        'HOST': os.environ.get('MYSQL_HOST', 'localhost'),
        'PORT': int(os.environ.get('MYSQL_PORT', '3306')),
        'USER': os.environ.get('MYSQL_USER', 'root'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
        'DATABASE': os.environ.get('MYSQL_DATABASE', 'medicine_db'),
        'CHARSET': os.environ.get('MYSQL_CHARSET', 'utf8mb4')
    },
    
    # 파일 및 디렉토리 설정
    'FILES': {
        'DATA_DIR': os.path.join('data'),
        'LOGS_DIR': os.path.join('logs'),
        'KEYWORDS_DIR': os.path.join('data', 'keywords'),
        'COLLECTED_DIR': os.path.join('data', 'collected'),
        'REPORTS_DIR': os.path.join('data', 'reports'),
        'TODO_KEYWORDS_FILE': os.path.join('data', 'keywords', 'todo.txt'),
        'DONE_KEYWORDS_FILE': os.path.join('data', 'keywords', 'done.txt'),
        'MEDICINE_IDS_FILE': os.path.join('data', 'collected', 'medicine_ids.txt'),
        'EXTRACTION_LOG_FILE': os.path.join('data', 'collected', 'extraction_log.txt'),
        'CHECKPOINT_FILE': os.path.join('data', 'checkpoint.json')
    },
    
    # 로깅 설정
    'LOGGING': {
        'LEVEL': os.environ.get('LOG_LEVEL', 'INFO'),
        'FORMAT': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        'DATE_FORMAT': '%Y-%m-%d %H:%M:%S',
        'MAX_SIZE': 5 * 1024 * 1024,  # 5MB
        'BACKUP_COUNT': 5
    },
    
    # 보고서 설정
    'REPORTS': {
        'BATCH_SIZE': 50,
        'TEMPLATE_DIR': os.path.join('src', 'reporting', 'templates'),
        'TEMPLATE_FILE': 'report_template.html'
    },
    
    # 추출 설정
    'EXTRACTION': {
        'SUCCESS_THRESHOLD': 0.8,  # 80% 이상 추출 시 성공
        'PARTIAL_THRESHOLD': 0.5,  # 50% 이상 추출 시 부분 성공
        'MIN_BASIC_FIELDS': 5,     # 최소 5개 이상의 기본 필드
        'MIN_DETAILED_FIELDS': 1   # 최소 1개 이상의 상세 필드
    }
}


# API 키 유효성 검사
def validate_api_keys():
    """
    API 키 유효성 검사
    
    Returns:
        bool: 유효성 여부
    """
    if not SETTINGS['API']['NAVER_CLIENT_ID'] or not SETTINGS['API']['NAVER_CLIENT_SECRET']:
        logger.error("네이버 API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return False
    
    return True


# 데이터베이스 설정 유효성 검사
def validate_database_settings():
    """
    데이터베이스 설정 유효성 검사
    
    Returns:
        bool: 유효성 여부
    """
    db_settings = SETTINGS['DATABASE']
    
    # 필수 설정 확인
    required_settings = ['HOST', 'PORT', 'USER', 'DATABASE']
    for setting in required_settings:
        if not db_settings.get(setting):
            logger.error(f"데이터베이스 설정 '{setting}'이(가) 누락되었습니다.")
            return False
    
    return True


# 전역 설정 업데이트
def update_settings(section: str, key: str, value: Any):
    """
    전역 설정 업데이트
    
    Args:
        section (str): 설정 섹션
        key (str): 설정 키
        value (any): 설정 값
    """
    if section in SETTINGS and key in SETTINGS[section]:
        SETTINGS[section][key] = value
        logger.debug(f"설정 업데이트: {section}.{key} = {value}")
    else:
        logger.warning(f"알 수 없는 설정: {section}.{key}")


# 설정 가져오기
def get_setting(section: str, key: str, default: Any = None) -> Any:
    """
    설정 가져오기
    
    Args:
        section (str): 설정 섹션
        key (str): 설정 키
        default (any, optional): 기본값
    
    Returns:
        설정 값 또는 기본값
    """
    if section in SETTINGS and key in SETTINGS[section]:
        return SETTINGS[section][key]
    else:
        return default


# 설정 로드 시 유효성 검사
def validate_settings():
    """설정 유효성 검사"""
    # 필수 디렉토리 확인
    for dir_key, dir_path in SETTINGS['FILES'].items():
        if dir_key.endswith('_DIR'):
            os.makedirs(dir_path, exist_ok=True)
    
    # API 키 유효성 검사
    if not validate_api_keys():
        logger.warning("API 키가 유효하지 않습니다. 일부 기능이 제한될 수 있습니다.")
    
    # 데이터베이스 설정 유효성 검사
    if not validate_database_settings():
        logger.warning("데이터베이스 설정이 유효하지 않습니다. 데이터베이스 기능이 제한될 수 있습니다.")


# 설정 초기화
validate_settings()