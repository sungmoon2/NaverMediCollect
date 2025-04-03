#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - main.py
생성일: 2025-04-03

메인 실행 스크립트로, 전체 프로그램의 진입점입니다.
명령행 인자를 처리하고 전체 실행 흐름을 관리합니다.
"""

import argparse
import sys
import os
import signal
import logging
from datetime import datetime
import time
import threading
from dotenv import load_dotenv  # 추가된 import

# .env 파일 로드 (추가된 부분)
load_dotenv()

# 내부 모듈 import
from src.api.naver_api import NaverApiHandler
from src.keyword.manager import KeywordManager
from src.data.extractor import DataExtractor
from src.database.connection import DBConnection
from src.utils.logger import setup_logger, log_section
from src.utils.checkpoint import CheckpointManager
from src.utils.safety import set_exit_handler
from src.reporting.html_reporter import HTMLReporter
from src.utils.file_manager import FileManager
from conf.settings import SETTINGS


def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(description='NaverMediCollect - 네이버 의약품 데이터 수집 도구')
    parser.add_argument('--keyword', type=str, help='시작할 키워드')
    parser.add_argument('--resume', action='store_true', help='마지막 체크포인트에서 재개')
    parser.add_argument('--max', type=int, default=0, help='최대 추출 의약품 수 (0=무제한)')
    parser.add_argument('--verbose', action='store_true', help='상세 로깅 활성화')
    parser.add_argument('--skip-db', action='store_true', help='데이터베이스 저장 건너뛰기')
    parser.add_argument('--report-only', action='store_true', help='기존 데이터로 보고서만 생성')
    return parser.parse_args()


def display_progress(running_event, extractor):
    """
    진행 상황을 주기적으로 표시하는 스레드 함수
    """
    while running_event.is_set():
        stats = extractor.get_stats()
        print(f"\r진행: {stats['total']}개 처리 (성공: {stats['success']}, 부분: {stats['partial']}, 실패: {stats['failed']})", end="")
        time.sleep(1)
    print()  # 줄바꿈으로 마무리


def main():
    args = parse_arguments()
    
    # 로깅 설정 (디버깅을 위해 DEBUG로 변경)
    log_level = logging.DEBUG  # args.verbose 대신 직접 DEBUG로 설정
    logger = setup_logger(log_level)
    logger.info(f"NaverMediCollect 시작 (시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    
    try:
        # 파일 관리자 초기화
        file_manager = FileManager()
        file_manager.ensure_directories()
        
        # 안전한 종료 핸들러 설정
        checkpoint_manager = CheckpointManager()
        set_exit_handler(checkpoint_manager.save_checkpoint)
        
        # 보고서만 생성하는 모드
        if args.report_only:
            logger.info("보고서 생성 모드로 실행 중...")
            html_reporter = HTMLReporter()
            html_reporter.generate_all_reports()
            logger.info("보고서 생성이 완료되었습니다.")
            return
        
        # 컴포넌트 초기화
        keyword_manager = KeywordManager()
        print(f"로드된 키워드: {keyword_manager.todo_keywords}")  # 디버깅 출력
        api_handler = NaverApiHandler()
        data_extractor = DataExtractor()
        html_reporter = HTMLReporter()
        
        # 데이터베이스 연결 (필요한 경우)
        db_connection = None if args.skip_db else DBConnection()
        
        # 시작 키워드 설정
        if args.resume:
            logger.info("마지막 체크포인트에서 재개합니다...")
            checkpoint = checkpoint_manager.load_checkpoint()
            if checkpoint:
                current_keyword = checkpoint.get('keyword')
                keyword_manager.set_current_keyword(current_keyword)
                logger.info(f"체크포인트에서 로드한 키워드: {current_keyword}")
            else:
                logger.warning("체크포인트를 찾을 수 없습니다. 첫 번째 키워드부터 시작합니다.")
        elif args.keyword:
            logger.info(f"지정된 키워드 '{args.keyword}'부터 시작합니다...")
            keyword_manager.set_current_keyword(args.keyword)
        else:
            logger.info("첫 번째 키워드부터 시작합니다...")
        
        # 진행 상황 표시 스레드 설정
        running_event = threading.Event()
        running_event.set()
        progress_thread = threading.Thread(target=display_progress, args=(running_event, data_extractor))
        progress_thread.daemon = True
        progress_thread.start()
        
        # 메인 데이터 수집 루프
        max_items = args.max if args.max > 0 else float('inf')
        total_processed = 0
        
        try:
            while total_processed < max_items:
                # 다음 키워드 가져오기
                keyword = keyword_manager.get_next_keyword()
                if not keyword:
                    logger.info("더 이상 처리할 키워드가 없습니다.")
                    break
                
                log_section(f"키워드 처리: {keyword}")
                
                # 네이버 API로 검색
                search_results = api_handler.search_keyword(keyword)
                
                if not search_results:
                    logger.warning(f"키워드 '{keyword}'에 대한 검색 결과가 없습니다.")
                    keyword_manager.mark_keyword_done(keyword)
                    continue
                
                # 검색 결과에서 의약품 데이터 추출
                for result in search_results:
                    # 최대 처리 개수 확인
                    if total_processed >= max_items:
                        break
                    
                    # 데이터 추출
                    medicine_id = result.get('medicine_id')
                    
                    # 이미 추출된 의약품인지 확인
                    if data_extractor.is_medicine_processed(medicine_id):
                        logger.debug(f"의약품 ID {medicine_id}는 이미 처리되었습니다. 건너뜁니다.")
                        continue
                    
                    # 데이터 추출 및 저장
                    extracted_data = data_extractor.extract_medicine_data(result)
                    
                    if extracted_data:
                        # 데이터베이스에 저장 (필요한 경우)
                        if db_connection:
                            db_connection.save_medicine_data(extracted_data)
                        
                        # 키워드 매니저 업데이트
                        new_keywords = data_extractor.extract_keywords_from_data(extracted_data)
                        keyword_manager.add_new_keywords(new_keywords)
                        
                        # 체크포인트 저장
                        checkpoint_manager.update_checkpoint(keyword=keyword, medicine_id=medicine_id)
                    
                    total_processed += 1
                
                # 현재 키워드 완료 처리
                keyword_manager.mark_keyword_done(keyword)
                
                # 일정 간격으로 보고서 생성
                if total_processed % 50 == 0:
                    html_reporter.generate_report_for_batch()
        
        finally:
            # 진행 상황 표시 스레드 종료
            running_event.clear()
            progress_thread.join()
        
        # 최종 보고서 생성
        html_reporter.generate_report_for_batch()
        
        logger.info(f"데이터 수집 프로세스 완료: 총 {total_processed}개 처리됨")
        
    except KeyboardInterrupt:
        logger.info("사용자에 의한 중단")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"예상치 못한 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()