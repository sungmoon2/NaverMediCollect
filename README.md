# NaverMediCollect

## 프로젝트 개요
네이버 검색 API를 활용한 의약품 데이터 수집 프로젝트입니다. 의약품 정보를 체계적으로 검색하고 추출하여 구조화된 데이터로 저장합니다.

## 설치 방법
```bash
# 저장소 클론
git clone <repository-url>
cd NaverMediCollect

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

>>>>    venv\Scripts\activate   <<<<


# 의존성 설치
pip install -r requirements.txt
```

## 사용 방법
```bash
# 기본 실행
python main.py

# 특정 키워드로 시작
python main.py --keyword "소화제"

# 체크포인트에서 재개
python main.py --resume

# 도움말
python main.py --help
```

## 주요 기능
- 키워드 기반 의약품 검색
- 21개 필드 자동 추출
- HTML 구조 보존
- 데이터 중복 방지
- 체크포인트를 통한 중단/재개
- HTML 보고서 생성

## 프로젝트 구조
```
NaverMediCollect/
├── main.py                     # 메인 실행 스크립트
├── src/                        # 소스 코드
│   ├── api/                    # API 관련 모듈
│   ├── data/                   # 데이터 처리 모듈
│   ├── database/               # 데이터베이스 모듈
│   ├── keyword/                # 키워드 관리 모듈
│   ├── parsing/                # HTML 파싱 모듈
│   ├── reporting/              # 보고서 생성 모듈
│   └── utils/                  # 유틸리티 모듈
├── conf/                       # 설정 파일
├── data/                       # 데이터 파일
└── logs/                       # 로그 파일
```

## 라이선스
This project is licensed under the MIT License - see the LICENSE file for details.
