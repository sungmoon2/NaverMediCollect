#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect 프로젝트 구조 생성 스크립트

이 스크립트는 NaverMediCollect 프로젝트에 필요한 디렉토리와 파일 구조를 자동으로 생성합니다.
"""

import os
import pathlib
import datetime


def create_directory(directory_path):
    """
    디렉토리를 생성하는 함수
    이미 존재하는 경우 생성하지 않음
    """
    path = pathlib.Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    print(f"디렉토리 생성: {directory_path}")


def create_file(file_path, content=""):
    """
    빈 파일을 생성하는 함수
    이미 존재하는 경우 덮어쓰지 않음
    """
    path = pathlib.Path(file_path)
    
    # 파일이 이미 존재하면 건너뜀
    if path.exists():
        print(f"파일 이미 존재: {file_path}")
        return
    
    # 디렉토리가 없으면 생성
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # 파일 작성
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"파일 생성: {file_path}")


def create_python_file(file_path, content=""):
    """
    Python 파일을 생성하는 함수 (기본 헤더 포함)
    """
    header = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NaverMediCollect - {os.path.basename(file_path)}
생성일: {datetime.datetime.now().strftime('%Y-%m-%d')}

"""

{content}
'''
    create_file(file_path, header)


def create_init_file(file_path):
    """
    __init__.py 파일을 생성하는 함수
    """
    content = f'''"""
NaverMediCollect - {os.path.dirname(file_path)} 패키지
"""
'''
    create_file(file_path, content)


def create_env_file():
    """
    .env 파일 생성
    """
    content = '''# Naver API 설정
NAVER_CLIENT_ID=u1WaLkN7noyDRj4OiCfV
NAVER_CLIENT_SECRET=h33N4vTMpw

# MySQL/MariaDB 설정
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=1234
MYSQL_DATABASE=medicine_db
MYSQL_CHARSET=utf8mb4

# 기타 설정
FLASK_SECRET_KEY=12341234
GEMINI_API_KEY=AIzaSyAA93TmOrNnWr0EgWASiX31FOCxPDmyT20
'''
    create_file('.env', content)


def create_gitignore_file():
    """
    .gitignore 파일 생성
    """
    content = '''# Log files
*.log

# Data directories
data/
logs/

# Report files
보고서.html

# Environment files
.env
.env.*

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual environment
venv/
.venv/
ENV/

# IDE specific
.vscode/
.idea/
*.swp
*.swo
.DS_Store
'''
    create_file('.gitignore', content)


def create_requirements_file():
    """
    requirements.txt 파일 생성
    """
    content = '''# API 요청 및 웹 관련
requests==2.31.0
beautifulsoup4==4.12.2
html5lib==1.1
bleach==6.1.0
lxml==4.9.3

# 데이터베이스
mysql-connector-python==8.3.0
SQLAlchemy==2.0.23

# 구성 및 환경
python-dotenv==1.0.0
PyYAML==6.0.1

# 데이터 처리
pandas==2.1.1
numpy==1.26.0

# 로깅 및 출력
colorama==0.4.6
tqdm==4.66.1
prettytable==3.9.0

# 파일 및 시스템
python-dateutil==2.8.2
openpyxl==3.1.2

# 유틸리티
retry==0.9.2
tenacity==8.2.3

# HTML 보고서 생성
jinja2==3.1.2
markdown==3.5

# 병렬 처리
aiohttp==3.9.1

# 테스트 및 개발
pytest==7.4.3
pytest-mock==3.12.0
'''
    create_file('requirements.txt', content)


def create_readme_file(project_name):
    """
    README.md 파일 생성
    """
    content = f'''# {project_name}

## 프로젝트 개요
네이버 검색 API를 활용한 의약품 데이터 수집 프로젝트입니다. 의약품 정보를 체계적으로 검색하고 추출하여 구조화된 데이터로 저장합니다.

## 설치 방법
```bash
# 저장소 클론
git clone <repository-url>
cd {project_name}

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

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
{project_name}/
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
'''
    create_file('README.md', content)


def create_venv_commands_file():
    """
    가상환경 명령어 안내 파일 생성
    """
    content = '''# 네이버 의약품 데이터 추출 프로젝트 가상환경 명령어

# 1. 가상환경 생성
## Windows
python -m venv venv

## macOS/Linux
python3 -m venv venv

# 2. 가상환경 활성화
## Windows
venv\\Scripts\\activate

## macOS/Linux
source venv/bin/activate

# 3. 의존성 패키지 설치
pip install -r requirements.txt

# 4. 가상환경 비활성화
deactivate

# 5. 프로젝트 실행
## 기본 실행
python main.py

## 특정 키워드로 시작
python main.py --keyword "소화제"

## 체크포인트에서 재개
python main.py --resume

## 도움말
python main.py --help
'''
    create_file('venv_commands.txt', content)


def create_main_py():
    """
    main.py 파일 생성
    """
    content = '''import argparse
import sys
import os
import signal
import logging
from datetime import datetime

# 내부 모듈 import
from src.api.naver_api import NaverApiHandler
from src.keyword.manager import KeywordManager
from src.data.extractor import DataExtractor
from src.database.connection import DBConnection
from src.utils.logger import setup_logger
from src.utils.checkpoint import CheckpointManager
from src.utils.safety import set_exit_handler
from src.reporting.html_reporter import HTMLReporter
from conf.settings import SETTINGS


def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(description='NaverMediCollect - 네이버 의약품 데이터 수집 도구')
    parser.add_argument('--keyword', type=str, help='시작할 키워드')
    parser.add_argument('--resume', action='store_true', help='마지막 체크포인트에서 재개')
    parser.add_argument('--max', type=int, default=0, help='최대 추출 의약품 수 (0=무제한)')
    parser.add_argument('--verbose', action='store_true', help='상세 로깅 활성화')
    return parser.parse_args()


def main():
    """메인 실행 함수"""
    args = parse_arguments()
    
    # 로깅 설정
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(log_level)
    logger.info(f"NaverMediCollect 시작 (시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    
    try:
        # 안전한 종료 핸들러 설정
        checkpoint_manager = CheckpointManager()
        set_exit_handler(checkpoint_manager.save_checkpoint)
        
        # 컴포넌트 초기화
        keyword_manager = KeywordManager()
        api_handler = NaverApiHandler()
        data_extractor = DataExtractor()
        db_connection = DBConnection()
        html_reporter = HTMLReporter()
        
        # TODO: 메인 실행 로직 구현
        logger.info("데이터 수집 프로세스 완료")
        
    except KeyboardInterrupt:
        logger.info("사용자에 의한 중단")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"예상치 못한 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
    create_python_file('main.py', content)


def create_template_file():
    """
    보고서 템플릿 파일 생성
    """
    content = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>의약품 데이터 추출 보고서 ({{ start_idx }}-{{ end_idx }})</title>
    <style>
        body {
            font-family: 'Malgun Gothic', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .report-header {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
            border-left: 5px solid #4b6cb7;
        }
        .medicine-item {
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .medicine-header {
            background-color: #f1f8ff;
            padding: 10px;
            margin: -15px -15px 15px -15px;
            border-bottom: 1px solid #ddd;
            border-radius: 5px 5px 0 0;
        }
        .field-name {
            font-weight: bold;
            color: #4b6cb7;
        }
        .success {
            color: #28a745;
        }
        .warning {
            color: #ffc107;
        }
        .error {
            color: #dc3545;
        }
        .stats {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div class="report-header">
        <h1>의약품 데이터 추출 보고서</h1>
        <p>생성 시간: {{ generation_time }}</p>
        <p>의약품 범위: {{ start_idx }} - {{ end_idx }}번</p>
    </div>

    <div class="stats">
        <h2>추출 통계</h2>
        <p>총 의약품 수: {{ total_medicines }}</p>
        <p>성공 추출: <span class="success">{{ successful_extractions }}</span></p>
        <p>부분 추출: <span class="warning">{{ partial_extractions }}</span></p>
        <p>실패 추출: <span class="error">{{ failed_extractions }}</span></p>
    </div>

    <h2>의약품 추출 목록</h2>
    
    {% for medicine in medicines %}
    <div class="medicine-item">
        <div class="medicine-header">
            <h3>{{ medicine.name }}</h3>
            <p>
                추출 상태: 
                {% if medicine.extraction_status == 'success' %}
                <span class="success">성공</span>
                {% elif medicine.extraction_status == 'partial' %}
                <span class="warning">부분</span>
                {% else %}
                <span class="error">실패</span>
                {% endif %}
            </p>
        </div>
        
        <table>
            <tr>
                <th>필드</th>
                <th>값</th>
                <th>상태</th>
            </tr>
            {% for field in medicine.fields %}
            <tr>
                <td class="field-name">{{ field.name }}</td>
                <td>
                    {% if field.value %}
                    {{ field.value|truncate(100) }}
                    {% else %}
                    -
                    {% endif %}
                </td>
                <td>
                    {% if field.status == 'success' %}
                    <span class="success">추출</span>
                    {% elif field.status == 'error' %}
                    <span class="error">실패</span>
                    {% else %}
                    <span class="warning">누락</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endfor %}

    <div>
        <p><strong>보고서 ID:</strong> {{ report_id }}</p>
    </div>
</body>
</html>
'''
    create_file('src/reporting/templates/report_template.html', content)


def main():
    """
    메인 실행 함수
    """
    project_name = "NaverMediCollect"
    print(f"{project_name} 프로젝트 구조 생성을 시작합니다...")
    
    # 기본 디렉토리 생성
    directories = [
        'src/api',
        'src/data',
        'src/database',
        'src/keyword',
        'src/parsing',
        'src/reporting/templates',
        'src/utils',
        'conf',
        'logs',
        'data/keywords',
        'data/collected',
        'data/reports',
        'tests/fixtures/sample_responses'
    ]
    
    for directory in directories:
        create_directory(directory)
    
    # __init__.py 파일 생성
    init_files = [
        'src/__init__.py',
        'src/api/__init__.py',
        'src/data/__init__.py',
        'src/database/__init__.py',
        'src/keyword/__init__.py',
        'src/parsing/__init__.py',
        'src/reporting/__init__.py',
        'src/utils/__init__.py',
        'conf/__init__.py',
        'tests/__init__.py',
    ]
    
    for init_file in init_files:
        create_init_file(init_file)
    
    # Python 소스 파일 생성
    python_files = [
        'src/api/naver_api.py',
        'src/data/extractor.py',
        'src/data/validator.py',
        'src/data/processor.py',
        'src/database/connection.py',
        'src/database/models.py',
        'src/database/operations.py',
        'src/keyword/manager.py',
        'src/keyword/generator.py',
        'src/parsing/html_parser.py',
        'src/parsing/field_mapper.py',
        'src/parsing/structure_preserver.py',
        'src/reporting/html_reporter.py',
        'src/utils/logger.py',
        'src/utils/checkpoint.py',
        'src/utils/file_manager.py',
        'src/utils/safety.py',
        'conf/settings.py',
        'conf/field_mapping.py',
        'tests/test_api.py',
        'tests/test_extractor.py',
        'tests/test_parser.py',
    ]
    
    for python_file in python_files:
        create_python_file(python_file)
    
    # 기타 필수 파일 생성
    create_env_file()
    create_gitignore_file()
    create_requirements_file()
    create_readme_file(project_name)
    create_venv_commands_file()
    create_main_py()
    create_template_file()
    
    # 데이터 파일 생성
    create_file('data/keywords/todo.txt', "소화제\n항생제\n진통제\n고혈압약\n당뇨병약")
    create_file('data/keywords/done.txt', "")
    create_file('data/collected/medicine_ids.txt', "")
    
    print(f"\n{project_name} 프로젝트 구조 생성이 완료되었습니다!")
    print(f"총 {len(directories)} 디렉토리, {len(init_files) + len(python_files) + 7} 파일이 생성되었습니다.")
    print("\n다음 단계를 진행하세요:")
    print("1. 가상환경을 생성하고 활성화합니다 (venv_commands.txt 참조)")
    print("2. 필요한 패키지를 설치합니다: pip install -r requirements.txt")
    print("3. main.py를 실행합니다: python main.py")


if __name__ == "__main__":
    main()