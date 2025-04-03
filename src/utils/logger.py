#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/utils/logger.py
생성일: 2025-04-03

로깅 설정 및 관리를 담당하는 모듈입니다.
컬러 로깅, 파일 로깅 등의 기능을 제공합니다.
"""

import os
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from colorama import init, Fore, Style


# Colorama 초기화
init(autoreset=True)


# 로그 색상 포맷 클래스
class ColoredFormatter(logging.Formatter):
    """색상이 적용된 로그 포맷터"""
    
    # 로그 레벨별 색상 지정
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    def format(self, record):
        """로그 메시지 포맷"""
        # 기본 포맷 적용
        log_message = super().format(record)
        
        # 레벨별 색상 적용
        levelname = record.levelname
        if levelname in self.COLORS:
            # 레벨명에 색상 적용
            colored_levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
            # 레벨명 교체
            log_message = log_message.replace(f"{levelname}: ", f"{colored_levelname}: ")
        
        return log_message


def setup_logger(level=logging.INFO, log_to_file=True):
    """
    로거 설정
    
    Args:
        level (int, optional): 로그 레벨. 기본값 logging.INFO
        log_to_file (bool, optional): 파일 로깅 여부. 기본값 True
        
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    # 로그 디렉토리 확인
    log_dir = os.path.join('logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 로거 객체 생성
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 콘솔 포맷 설정 (색상 적용)
    console_format = "%(asctime)s [%(levelname)s]: %(message)s"
    console_datefmt = "%H:%M:%S"
    console_formatter = ColoredFormatter(console_format, datefmt=console_datefmt)
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(console_handler)
    
    # 파일 로깅 활성화
    if log_to_file:
        # 파일 핸들러 추가 (로테이팅 방식)
        today = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"extraction_{today}.log")
        
        # 최대 5MB, 최대 5개 백업 파일
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(level)
        
        # 파일 포맷 설정 (색상 미적용)
        file_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        
        logger.addHandler(file_handler)
        
        # 오류 전용 로그 파일
        error_log_file = os.path.join(log_dir, f"error_{today}.log")
        error_handler = RotatingFileHandler(
            error_log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        logger.addHandler(error_handler)
    
    return logger


def log_section(title, char='━', width=50):
    """
    섹션 구분선 로깅
    
    Args:
        title (str): 섹션 제목
        char (str, optional): 구분선 문자. 기본값 '━'
        width (int, optional): 구분선 너비. 기본값 50
    """
    logger = logging.getLogger()
    
    # 상단 구분선
    logger.info(char * width)
    
    # 제목
    if title:
        logger.info(f"{title}")
    
    # 하단 구분선
    logger.info(char * width)


def log_medicine_extraction(medicine_name, fields_count, total_fields, missing_fields=None, status='success'):
    """
    의약품 추출 정보 로깅
    
    Args:
        medicine_name (str): 의약품 이름
        fields_count (int): 추출된 필드 수
        total_fields (int): 전체 필드 수
        missing_fields (list, optional): 누락된 필드 목록
        status (str, optional): 추출 상태. 기본값 'success'
    """
    logger = logging.getLogger()
    
    # 상단 구분선
    logger.info('━' * 50)
    
    # 기본 정보
    logger.info(f"🔍 의약품 추출: {medicine_name}")
    logger.info(f"- 총 필드: {total_fields} / 추출 필드: {fields_count}")
    
    # 누락 필드
    if missing_fields:
        logger.info(f"- 누락 필드: {', '.join(missing_fields)}")
    
    # 상태
    status_icon = '✅' if status == 'success' else '⚠️' if status == 'partial' else '❌'
    status_text = '성공' if status == 'success' else '부분' if status == 'partial' else '실패'
    logger.info(f"- 상태: {status_icon} {status_text}")
    
    # 하단 구분선
    logger.info('━' * 50)