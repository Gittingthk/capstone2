# 세포 배양 자동화 시스템

## 설치 방법

1. Anaconda 설치
   - [Anaconda 공식 웹사이트](https://www.anaconda.com/products/distribution)에서 다운로드
   - Windows의 경우 "Windows installer"를 다운로드하여 실행
   - 설치 과정에서 "Add Anaconda to my PATH environment variable" 옵션을 체크

2. Conda 환경 생성 및 패키지 설치
   ```bash
   # 프로젝트 디렉토리로 이동
   cd 캡스톤디자인

   # Conda 환경 생성 및 패키지 설치
   conda env create -f environment.yml

   # 환경 활성화
   conda activate cell_culture_automation
   ```

## 실행 방법

1. Arduino 코드 업로드
   - Arduino IDE를 실행
   - `src/arduino/cell_culture_controller/cell_culture_controller.ino` 파일 열기
   - Arduino 보드에 업로드

2. Raspberry Pi 프로그램 실행
   ```bash
   # 환경이 활성화되어 있지 않다면:
   conda activate cell_culture_automation

   # 프로그램 실행
   cd src/raspberry_pi
   python main.py
   ```

3. 웹 인터페이스 접속
   - 브라우저에서 `http://localhost:5000` 접속
   - 또는 라즈베리파이 IP 주소로 접속 (예: `http://192.168.1.100:5000`)

## 주의사항

- Arduino와 Raspberry Pi가 올바르게 연결되어 있는지 확인
- 카메라가 정상적으로 연결되어 있는지 확인
- 모든 기계 부품이 안전하게 설치되어 있는지 확인

## 문제 해결

- 환경 활성화가 안될 경우:
  ```bash
  conda deactivate
  conda activate cell_culture_automation
  ```

- 패키지 설치 오류 발생 시:
  ```bash
  conda env remove -n cell_culture_automation
  conda env create -f environment.yml
  ``` 