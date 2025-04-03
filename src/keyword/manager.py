#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/keyword/manager.py
생성일: 2025-04-03

의약품 검색 키워드 관리를 담당하는 모듈입니다.
키워드 로드, 추가, 완료 처리 등의 기능을 제공합니다.
"""

import os
import logging
import random
from typing import List, Set, Optional
from src.utils.file_manager import FileManager


class KeywordManager:
    """키워드 관리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        self.file_manager = FileManager()
        
        # 파일 경로
        self.todo_path = os.path.join('data', 'keywords', 'todo.txt')
        self.done_path = os.path.join('data', 'keywords', 'done.txt')
        
        # 키워드 집합
        self.todo_keywords = set()
        self.done_keywords = set()
        
        # 현재 처리 중인 키워드
        self.current_keyword = None
        
        # 디렉토리 확인 및 초기 로드
        self._ensure_directories()
        self._load_keywords()
    
    def _ensure_directories(self):
        """키워드 파일 디렉토리 확인"""
        os.makedirs(os.path.dirname(self.todo_path), exist_ok=True)
        
        # 파일이 없으면 빈 파일 생성
        if not os.path.exists(self.todo_path):
            with open(self.todo_path, 'w', encoding='utf-8') as f:
                f.write("소화제\n항생제\n진통제\n고혈압약\n당뇨병약\n")
            
            self.logger.info(f"기본 키워드 목록 생성됨: {self.todo_path}")
        
        if not os.path.exists(self.done_path):
            with open(self.done_path, 'w', encoding='utf-8') as f:
                pass
            
            self.logger.info(f"완료 키워드 파일 생성됨: {self.done_path}")
    
    def _load_keywords(self):
        """키워드 파일에서 키워드 로드"""
        # 처리할 키워드 로드
        if os.path.exists(self.todo_path):
            with open(self.todo_path, 'r', encoding='utf-8') as f:
                for line in f:
                    keyword = line.strip()
                    if keyword:
                        self.todo_keywords.add(keyword)
        
        # 완료된 키워드 로드
        if os.path.exists(self.done_path):
            with open(self.done_path, 'r', encoding='utf-8') as f:
                for line in f:
                    keyword = line.strip()
                    if keyword:
                        self.done_keywords.add(keyword)
        
        self.logger.info(f"키워드 로드 완료: 처리할 키워드 {len(self.todo_keywords)}개, 완료된 키워드 {len(self.done_keywords)}개")
    
    def get_next_keyword(self) -> Optional[str]:
        """
        다음 처리할 키워드 가져오기
        
        Returns:
            str: 다음 키워드 (없으면 None)
        """
        # 현재 처리 중인 키워드가 있으면 반환
        if self.current_keyword:
            return self.current_keyword
        
        # 처리할 키워드가 없으면 None 반환
        if not self.todo_keywords:
            return None
        
        # 다음 키워드 선택
        self.current_keyword = random.choice(list(self.todo_keywords))
        
        return self.current_keyword
    
    def set_current_keyword(self, keyword: str):
        """
        현재 처리 중인 키워드 설정
        
        Args:
            keyword (str): 설정할 키워드
        """
        if not keyword:
            return
        
        # 이미 완료된 키워드인지 확인
        if keyword in self.done_keywords:
            self.logger.warning(f"키워드 '{keyword}'는 이미 완료되었습니다.")
            return
        
        # todo 목록에 없으면 추가
        if keyword not in self.todo_keywords:
            self.add_new_keywords([keyword])
        
        # 현재 키워드 설정
        self.current_keyword = keyword
        self.logger.info(f"현재 키워드 설정: {keyword}")
    
    def mark_keyword_done(self, keyword: str):
        """
        키워드를 완료 처리
        
        Args:
            keyword (str): 완료 처리할 키워드
        """
        if not keyword:
            return
        
        # 처리할 키워드 목록에서 제거
        if keyword in self.todo_keywords:
            self.todo_keywords.remove(keyword)
        
        # 완료 목록에 추가
        if keyword not in self.done_keywords:
            self.done_keywords.add(keyword)
            
            # 완료 파일에 추가
            with open(self.done_path, 'a', encoding='utf-8') as f:
                f.write(f"{keyword}\n")
        
        # 현재 키워드가 완료된 경우 초기화
        if self.current_keyword == keyword:
            self.current_keyword = None
        
        # todo 파일 업데이트
        self._update_todo_file()
        
        self.logger.info(f"키워드 완료 처리: {keyword}")
    
    def add_new_keywords(self, keywords: List[str]):
        """
        새 키워드 추가
        
        Args:
            keywords (list): 추가할 키워드 목록
        """
        if not keywords:
            return
        
        new_count = 0
        
        for keyword in keywords:
            # 공백 및 중복 검사
            if not keyword or keyword in self.todo_keywords or keyword in self.done_keywords:
                continue
            
            # 처리할 키워드 목록에 추가
            self.todo_keywords.add(keyword)
            new_count += 1
        
        if new_count > 0:
            # todo 파일 업데이트
            self._update_todo_file()
            
            self.logger.info(f"새 키워드 {new_count}개 추가됨")
    
    def _update_todo_file(self):
        """todo 파일 업데이트"""
        with open(self.todo_path, 'w', encoding='utf-8') as f:
            for keyword in self.todo_keywords:
                f.write(f"{keyword}\n")
    
    def get_keyword_counts(self) -> dict:
        """
        키워드 통계 정보 반환
        
        Returns:
            dict: 키워드 통계
        """
        return {
            'todo': len(self.todo_keywords),
            'done': len(self.done_keywords),
            'total': len(self.todo_keywords) + len(self.done_keywords)
        }