#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/utils/file_manager.py
생성일: 2025-04-03

파일 및 디렉토리 관리를 담당하는 모듈입니다.
파일 생성, 읽기, 쓰기 등의 기능을 제공합니다.
"""

import os
import logging
import json
import csv
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, TextIO


class FileManager:
    """파일 관리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 기본 디렉토리 정보
        self.project_dir = os.path.abspath(os.path.curdir)
        self.data_dir = os.path.join(self.project_dir, 'data')
        self.logs_dir = os.path.join(self.project_dir, 'logs')
        self.keywords_dir = os.path.join(self.data_dir, 'keywords')
        self.collected_dir = os.path.join(self.data_dir, 'collected')
        self.reports_dir = os.path.join(self.data_dir, 'reports')
    
    def ensure_directories(self):
        """필요한 디렉토리 생성"""
        directories = [
            self.data_dir,
            self.logs_dir,
            self.keywords_dir,
            self.collected_dir,
            self.reports_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.logger.debug(f"디렉토리 확인: {directory}")
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        파일 읽기
        
        Args:
            file_path (str): 파일 경로
            encoding (str, optional): 인코딩. 기본값 'utf-8'
            
        Returns:
            str: 파일 내용 (실패 시 빈 문자열)
        """
        if not os.path.exists(file_path):
            self.logger.warning(f"파일이 존재하지 않습니다: {file_path}")
            return ""
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return content
            
        except Exception as e:
            self.logger.error(f"파일 읽기 오류 ({file_path}): {e}")
            return ""
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8', mode: str = 'w') -> bool:
        """
        파일 쓰기
        
        Args:
            file_path (str): 파일 경로
            content (str): 파일 내용
            encoding (str, optional): 인코딩. 기본값 'utf-8'
            mode (str, optional): 파일 모드. 기본값 'w'
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 디렉토리 확인
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"파일 쓰기 오류 ({file_path}): {e}")
            return False
    
    def append_to_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        파일에 내용 추가
        
        Args:
            file_path (str): 파일 경로
            content (str): 추가할 내용
            encoding (str, optional): 인코딩. 기본값 'utf-8'
            
        Returns:
            bool: 성공 여부
        """
        return self.write_file(file_path, content, encoding, 'a')
    
    def read_json(self, file_path: str, encoding: str = 'utf-8') -> Optional[Union[Dict, List]]:
        """
        JSON 파일 읽기
        
        Args:
            file_path (str): 파일 경로
            encoding (str, optional): 인코딩. 기본값 'utf-8'
            
        Returns:
            dict or list: JSON 데이터 (실패 시 None)
        """
        if not os.path.exists(file_path):
            self.logger.warning(f"JSON 파일이 존재하지 않습니다: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                data = json.load(f)
            
            return data
            
        except Exception as e:
            self.logger.error(f"JSON 파일 읽기 오류 ({file_path}): {e}")
            return None
    
    def write_json(self, file_path: str, data: Union[Dict, List], encoding: str = 'utf-8', indent: int = 2) -> bool:
        """
        JSON 파일 쓰기
        
        Args:
            file_path (str): 파일 경로
            data (dict or list): JSON 데이터
            encoding (str, optional): 인코딩. 기본값 'utf-8'
            indent (int, optional): 들여쓰기. 기본값 2
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 디렉토리 확인
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            
            return True
            
        except Exception as e:
            self.logger.error(f"JSON 파일 쓰기 오류 ({file_path}): {e}")
            return False
    
    def read_csv(self, file_path: str, encoding: str = 'utf-8') -> List[Dict[str, str]]:
        """
        CSV 파일 읽기
        
        Args:
            file_path (str): 파일 경로
            encoding (str, optional): 인코딩. 기본값 'utf-8'
            
        Returns:
            list: CSV 데이터 (실패 시 빈 리스트)
        """
        if not os.path.exists(file_path):
            self.logger.warning(f"CSV 파일이 존재하지 않습니다: {file_path}")
            return []
        
        try:
            data = []
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            
            return data
            
        except Exception as e:
            self.logger.error(f"CSV 파일 읽기 오류 ({file_path}): {e}")
            return []
    
    def write_csv(self, file_path: str, data: List[Dict[str, str]], fieldnames: Optional[List[str]] = None, encoding: str = 'utf-8') -> bool:
        """
        CSV 파일 쓰기
        
        Args:
            file_path (str): 파일 경로
            data (list): CSV 데이터 (딕셔너리 목록)
            fieldnames (list, optional): 필드명 목록. 기본값 None (첫 번째 행에서 추출)
            encoding (str, optional): 인코딩. 기본값 'utf-8'
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 데이터가 없으면 빈 파일 생성
            if not data:
                with open(file_path, 'w', encoding=encoding, newline='') as f:
                    f.write('')
                return True
            
            # 필드명이 없으면 첫 번째 행에서 추출
            if not fieldnames:
                fieldnames = list(data[0].keys())
            
            # 디렉토리 확인
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding, newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"CSV 파일 쓰기 오류 ({file_path}): {e}")
            return False
    
    def append_to_csv(self, file_path: str, row: Dict[str, str], fieldnames: Optional[List[str]] = None, encoding: str = 'utf-8') -> bool:
        """
        CSV 파일에 행 추가
        
        Args:
            file_path (str): 파일 경로
            row (dict): 추가할 행 데이터
            fieldnames (list, optional): 필드명 목록. 기본값 None (파일에서 추출 또는 행에서 추출)
            encoding (str, optional): 인코딩. 기본값 'utf-8'
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 디렉토리 확인
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # 파일이 없으면 새로 생성
            if not os.path.exists(file_path):
                # 필드명이 없으면 행에서 추출
                if not fieldnames:
                    fieldnames = list(row.keys())
                
                with open(file_path, 'w', encoding=encoding, newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow(row)
            else:
                # 기존 파일에 행 추가
                # 필드명이 없으면 파일에서 추출
                if not fieldnames:
                    with open(file_path, 'r', encoding=encoding, newline='') as f:
                        reader = csv.reader(f)
                        fieldnames = next(reader)
                
                with open(file_path, 'a', encoding=encoding, newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(row)
            
            return True
            
        except Exception as e:
            self.logger.error(f"CSV 파일에 행 추가 오류 ({file_path}): {e}")
            return False
    
    def read_lines(self, file_path: str, strip: bool = True, encoding: str = 'utf-8') -> List[str]:
        """
        파일을 행 단위로 읽기
        
        Args:
            file_path (str): 파일 경로
            strip (bool, optional): 공백 제거 여부. 기본값 True
            encoding (str, optional): 인코딩. 기본값 'utf-8'
            
        Returns:
            list: 행 목록 (실패 시 빈 리스트)
        """
        if not os.path.exists(file_path):
            self.logger.warning(f"파일이 존재하지 않습니다: {file_path}")
            return []
        
        try:
            lines = []
            with open(file_path, 'r', encoding=encoding) as f:
                for line in f:
                    if strip:
                        line = line.strip()
                    
                    if line:  # 빈 행 제외
                        lines.append(line)
            
            return lines
            
        except Exception as e:
            self.logger.error(f"파일 행 읽기 오류 ({file_path}): {e}")
            return []
    
    def write_lines(self, file_path: str, lines: List[str], encoding: str = 'utf-8', mode: str = 'w') -> bool:
        """
        파일에 행 목록 쓰기
        
        Args:
            file_path (str): 파일 경로
            lines (list): 행 목록
            encoding (str, optional): 인코딩. 기본값 'utf-8'
            mode (str, optional): 파일 모드. 기본값 'w'
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 디렉토리 확인
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(file_path, mode, encoding=encoding) as f:
                for line in lines:
                    f.write(f"{line}\n")
            
            return True
            
        except Exception as e:
            self.logger.error(f"파일 행 쓰기 오류 ({file_path}): {e}")
            return False
    
    def get_timestamp(self) -> str:
        """
        현재 타임스탬프 반환
        
        Returns:
            str: ISO 형식 타임스탬프
        """
        return datetime.now().isoformat()