#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - src/database/models.py
생성일: 2025-04-03

데이터베이스 모델 정의 모듈입니다.
테이블 구조에 맞는 클래스와 메서드를 제공합니다.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class MedicineBasicInfo:
    """의약품 기본 정보 모델"""
    
    medicine_id: str
    name_ko: str
    name_en: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    company: Optional[str] = None
    insurance_code: Optional[str] = None
    appearance: Optional[str] = None
    formulation: Optional[str] = None
    shape: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    identification: Optional[str] = None
    dividing_line: Optional[str] = None
    ingredient_info: Optional[str] = None
    storage_method: Optional[str] = None
    usage_period: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MedicineBasicInfo':
        """
        딕셔너리에서 모델 객체 생성
        
        Args:
            data (dict): 의약품 기본 정보 딕셔너리
            
        Returns:
            MedicineBasicInfo: 생성된 모델 객체
        """
        # 필수 필드 검증
        if 'medicine_id' not in data or 'name_ko' not in data:
            raise ValueError("필수 필드가 누락되었습니다: medicine_id, name_ko")
        
        # 날짜 필드 변환
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        
        # 모델에 없는 필드 제거
        valid_fields = cls.__annotations__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        모델 객체를 딕셔너리로 변환
        
        Returns:
            dict: 변환된 딕셔너리
        """
        result = {}
        
        for key, value in self.__dict__.items():
            # 날짜 필드는 문자열로 변환
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        
        return result


@dataclass
class MedicineDetailedInfo:
    """의약품 상세 정보 모델"""
    
    medicine_id: str
    effectiveness: Optional[str] = None
    dosage: Optional[str] = None
    precautions: Optional[str] = None
    professional_precautions: Optional[str] = None
    effectiveness_html: Optional[str] = None
    dosage_html: Optional[str] = None
    precautions_html: Optional[str] = None
    professional_precautions_html: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MedicineDetailedInfo':
        """
        딕셔너리에서 모델 객체 생성
        
        Args:
            data (dict): 의약품 상세 정보 딕셔너리
            
        Returns:
            MedicineDetailedInfo: 생성된 모델 객체
        """
        # 필수 필드 검증
        if 'medicine_id' not in data:
            raise ValueError("필수 필드가 누락되었습니다: medicine_id")
        
        # 날짜 필드 변환
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        
        # 모델에 없는 필드 제거
        valid_fields = cls.__annotations__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        모델 객체를 딕셔너리로 변환
        
        Returns:
            dict: 변환된 딕셔너리
        """
        result = {}
        
        for key, value in self.__dict__.items():
            # 날짜 필드는 문자열로 변환
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        
        return result


@dataclass
class Medicine:
    """통합 의약품 정보 모델"""
    
    basic_info: MedicineBasicInfo
    detailed_info: Optional[MedicineDetailedInfo] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Medicine':
        """
        딕셔너리에서 모델 객체 생성
        
        Args:
            data (dict): 의약품 통합 정보 딕셔너리
            
        Returns:
            Medicine: 생성된 모델 객체
        """
        if 'basic_info' not in data:
            raise ValueError("기본 정보가 누락되었습니다")
        
        basic_info = MedicineBasicInfo.from_dict(data['basic_info'])
        
        detailed_info = None
        if 'detailed_info' in data and data['detailed_info']:
            detailed_info = MedicineDetailedInfo.from_dict(data['detailed_info'])
        
        return cls(basic_info=basic_info, detailed_info=detailed_info)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        모델 객체를 딕셔너리로 변환
        
        Returns:
            dict: 변환된 딕셔너리
        """
        result = {
            'basic_info': self.basic_info.to_dict()
        }
        
        if self.detailed_info:
            result['detailed_info'] = self.detailed_info.to_dict()
        else:
            result['detailed_info'] = {}
        
        return result