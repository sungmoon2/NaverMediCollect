import venv
import os
import sys
import subprocess

# 가상환경 이름 설정
venv_name = "venv"  # 원하는 가상환경 이름으로 변경 가능

# 현재 디렉토리에 가상환경 생성
venv_path = os.path.join(os.getcwd(), venv_name)
venv.create(venv_path, with_pip=True)

print(f"✅ 가상환경이 생성되었습니다: {venv_path}")

# 가상환경에서 pip 업그레이드
pip_path = os.path.join(venv_path, "Scripts" if os.name == "nt" else "bin", "pip")
subprocess.run([pip_path, "install", "--upgrade", "pip"])

print("✅ pip가 최신 버전으로 업그레이드되었습니다.")

# 가상환경 활성화 안내
if os.name == "nt":
    print(f"🔹 Windows에서 가상환경 활성화: {venv_name}\\Scripts\\activate")
else:
    print(f"🔹 macOS/Linux에서 가상환경 활성화: source {venv_name}/bin/activate")
