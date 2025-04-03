#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/utils/checkpoint.py
생성일: 2025-04-03

체크포인트 관리를 담당하는 모듈입니다.
중단 지점 저장 및 불러오기 기능을 제공합니다.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional


class CheckpointManager:
    """체크포인트 관리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 체크포인트 파일 경로
        self.checkpoint_dir = os.path.join('data')
        self.checkpoint_file = os.path.join(self.checkpoint_dir, 'checkpoint.json')
        
        # 체크포인트 데이터
        self.checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'keyword': None,
            'medicine_id': None,
            'stats': {
                'total': 0,
                'success': 0,
                'partial': 0,
                'failed': 0
            }
        }
        
        # 디렉토리 생성
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # 기존 체크포인트 로드
        self._load_checkpoint()
    
    def _load_checkpoint(self):
        """체크포인트 파일 로드"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 유효한 데이터만 로드
                    if isinstance(data, dict):
                        # 기본 필드 확인 및 설정
                        for key in self.checkpoint_data:
                            if key in data:
                                self.checkpoint_data[key] = data[key]
                
                self.logger.info(f"체크포인트 로드됨: {self.checkpoint_file}")
                
            except Exception as e:
                self.logger.error(f"체크포인트 로드 오류: {e}")
    
    def update_checkpoint(self, **kwargs):
        """
        체크포인트 데이터 업데이트
        
        Args:
            **kwargs: 업데이트할 필드 (keyword, medicine_id, stats 등)
        """
        # 타임스탬프 업데이트
        self.checkpoint_data['timestamp'] = datetime.now().isoformat()
        
        # 지정된 필드 업데이트
        for key, value in kwargs.items():
            if key in self.checkpoint_data:
                self.checkpoint_data[key] = value
            elif key == 'stats' and isinstance(value, dict):
                # stats 딕셔너리 업데이트
                for stat_key, stat_value in value.items():
                    if stat_key in self.checkpoint_data['stats']:
                        self.checkpoint_data['stats'][stat_key] = stat_value
        
        # 체크포인트 저장
        self.save_checkpoint()
    
    def save_checkpoint(self):
        """체크포인트 파일 저장"""
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(self.checkpoint_data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"체크포인트 저장됨: {self.checkpoint_file}")
            
        except Exception as e:
            self.logger.error(f"체크포인트 저장 오류: {e}")
    
    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        체크포인트 로드
        
        Returns:
            dict: 체크포인트 데이터 (없으면 None)
        """
        # 체크포인트 파일 확인
        if not os.path.exists(self.checkpoint_file):
            self.logger.warning("체크포인트 파일이 없습니다.")
            return None
        
        # 이미 로드된 데이터 반환
        return self.checkpoint_data
    
    def reset_checkpoint(self):
        """체크포인트 초기화"""
        # 체크포인트 데이터 초기화
        self.checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'keyword': None,
            'medicine_id': None,
            'stats': {
                'total': 0,
                'success': 0,
                'partial': 0,
                'failed': 0
            }
        }
        
        # 체크포인트 저장
        self.save_checkpoint()
        
        self.logger.info("체크포인트가 초기화되었습니다.")
    
    def backup_checkpoint(self):
        """체크포인트 백업"""
        if not os.path.exists(self.checkpoint_file):
            self.logger.warning("백업할 체크포인트 파일이 없습니다.")
            return
        
        # 백업 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.checkpoint_dir, f"checkpoint_{timestamp}.json")
        
        try:
            # 체크포인트 파일 복사
            with open(self.checkpoint_file, 'r', encoding='utf-8') as src:
                with open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            self.logger.info(f"체크포인트 백업 생성됨: {backup_file}")
            
        except Exception as e:
            self.logger.error(f"체크포인트 백업 오류: {e}")