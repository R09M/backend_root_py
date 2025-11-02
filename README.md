# 🌱 라즈베리파이, 파이썬 기반 스마트팜 IoT 기기 개발 및 빅데이터 수집 알고리즘 개발

[![Notion](https://img.shields.io/badge/Notion-Details-F7F6F3?style=flat&logo=notion&logoColor=000000)](https://is.gd/NLSbOP)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4-A22846?style=flat&logo=raspberrypi&logoColor=white)](https://www.raspberrypi.org/)
[![MariaDB](https://img.shields.io/badge/MariaDB-10.x-003545?style=flat&logo=mariadb&logoColor=white)](https://mariadb.org/)
[![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-010101?style=flat&logo=socketdotio&logoColor=white)](https://websockets.readthedocs.io/)

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [시스템 구조](#-시스템-구조)
- [시작하기](#-시작하기)
- [주요 성과](#-주요-성과)
- [트러블슈팅](#-트러블슈팅)
- [프로젝트 통계](#-프로젝트-통계)
- [라이선스](#-라이선스)

## 📌 프로젝트 개요

**개발 기간** : 2025.09.15 ~ 2025.10.31 (47일)

**프로젝트 목표** : 농작물 생육을 위한 IoT 기반 환경 모니터링 및 자동 제어 시스템 구축

**핵심 성과** :
- 실시간 센서 데이터 수집 및 자동 제어 시스템 완성
- 데이터베이스 저장 최적화로 **99.6% 효율 개선** (120회 → 1회)
- WebSocket 기반 모바일 원격 제어 구현
- 30개 이상의 실질적 문제 해결 경험

## ✨ 주요 기능

### 1️⃣ 환경 센서 시스템
DHT22 온습도, FC-28 토양수분, LDR 조도, PIR 모션 센서를 통합하여 실시간 환경 데이터를 수집합니다.

**주요 성과**
- 센서 안정성 30% → 거의 100%
- 실시간 측정(1분)과 DB 저장(1시간) 주기 분리
- SPI 통신으로 아날로그 센서 데이터 수집

### 2️⃣ 자동 제어 시스템
조도 기반 LED 제어, 시간대별 팬 제어(낮 20°C, 밤 10°C), 히스테리시스 방식 워터펌프 제어(60~75%)를 구현했습니다.

**주요 성과**
- 농촌진흥청 농작물 생육 기준 적용
- 시간대별 온도 관리로 일교차 활용
- 히스테리시스 제어로 장치 수명 연장

### 3️⃣ 데이터베이스 관리
환경 데이터와 제어 상태를 별도 테이블로 분리하고, 상태 변화 감지 로직으로 DB 저장 횟수를 99.6% 감소시켰습니다.

**주요 성과**
- DB 저장 99.6% 감소 (120회 → 1회)
- 테이블 분리로 데이터 구조 효율화
- 공통 모듈화로 코드 중복 제거

### 4️⃣ 실시간 원격 제어 시스템
WebSocket 기반 양방향 통신으로 모바일 앱에서 센서 데이터를 실시간 조회하고 장치를 원격 제어할 수 있습니다.

**주요 성과**
- asyncio 기반 비동기 WebSocket 서버 구현
- 다중 클라이언트 동시 접속 지원
- 공유 메모리로 DB 부하 완전 제거

### 5️⃣ 계층별 설정 관리 시스템
하드웨어 설정, 농작물 환경 설정, 사용자 설정을 3단계 계층으로 분리하여 관리합니다.

**주요 성과**
- 3단계 설정 계층 구조 확립
- JSON 기반 동적 설정 관리
- 프로그램 재시작 없이 실시간 변경

### 6️⃣ 멀티스레드 통합 시스템
5개 독립 스레드가 동시에 실행되며, 각 기능이 독립적으로 동작합니다.

**주요 성과**
- 5개 독립 스레드 동시 실행
- 공유 메모리 기반 데이터 교환
- 안전한 리소스 정리 및 종료 처리

## 🔧 기술 스택

### 하드웨어
- **메인보드** : Raspberry Pi 4
- **센서** : DHT22 (온습도), FC-28 (토양수분), LDR (조도), PIR (모션)
- **제어** : LED, 팬 모터, 워터펌프, 부저
- **통신** : SPI (MCP3008 ADC), GPIO

### 소프트웨어
- **언어** : Python 3.11
- **데이터베이스** : MariaDB
- **네트워크** : WebSocket
- **아키텍처** : 멀티스레드 (5개 스레드 동시 실행)

## 🏗️ 시스템 구조

### 파일 구조
```
📦 프로젝트
├── 📄 constant.py          # 하드웨어 설정
├── 📄 config_manager.py    # 사용자 설정 관리
├── 📄 crop_config.py       # 농작물별 환경 설정
├── 📄 db_utils.py          # 데이터베이스 공통 모듈
├── 📄 multi_sensor.py      # 환경 센서 통합
├── 📄 multi_control.py     # 자동 제어 시스템
├── 📄 motion_detector.py   # 모션 감지 + 부저
├── 📄 websocket_server.py  # 웹소켓 통신
└── 📄 integrated_system.py # 5개 스레드 통합 관리
```

### 전체 아키텍처
```
라즈베리파이 통합 시스템
├── 센서 체크 스레드 (1분 주기) → 실시간 데이터 수집
├── 센서 저장 스레드 (1시간 주기) → DB 저장
├── 자동 제어 스레드 (5분 주기) → LED, 팬, 펌프 제어
├── 모션 감지 스레드 (1초 주기) → 보안 알람
└── 웹소켓 서버 (항시) → 원격 통신
```

### 데이터베이스 구조
```sql
-- 환경 데이터 (1시간마다 저장)
GROWING_ENVIRONMENT (온도, 습도, 토양수분, 조도)

-- 제어 상태 (상태 변화 시 저장)
DEVICE_STATUS (모션, 팬, 펌프, LED)
```

## 🚀 시작하기

### 시스템 요구사항
- Raspberry Pi 4 (권장)
- Python 3.11 이상
- MariaDB 10.x
- 필수 하드웨어 : DHT22, FC-28, LDR, PIR, MCP3008

### 설치 방법

#### Python 패키지 설치
```bash
pip install RPi.GPIO adafruit-circuitpython-dht spidev pymysql websockets
```

#### MariaDB 설정
```sql
-- 데이터베이스 생성
CREATE DATABASE ...;

-- 환경 데이터 테이블
CREATE TABLE GROWING_ENVIRONMENT(
    TEMPER_NUM INT PRIMARY KEY AUTO_INCREMENT,
    TEMPER FLOAT NOT NULL,
    HUMIDITY FLOAT NOT NULL,
    SOIL_HUMIDITY FLOAT NOT NULL, 
    ILLUMINATION INT NOT NULL,
    CREATE_DATE DATETIME DEFAULT SYSDATE()
);

-- 제어 상태 테이블
CREATE TABLE DEVICE_STATUS (
    STATUS_ID INT PRIMARY KEY AUTO_INCREMENT,
    TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP,
    MOTION_DETECTED TINYINT(1) DEFAULT 0,
    FAN_MOTOR TINYINT(1) DEFAULT 0,
    WATER_PUMP TINYINT(1) DEFAULT 0,
    LED_LIGHT TINYINT(1) DEFAULT 0
);
```

#### 설정 파일 수정
`constant.py`의 `DATABASE_CONFIG`를 본인의 환경에 맞게 수정하세요 :
```python
DATABASE_CONFIG = {
    'host': '...',
    'user': '...',
    'password': '...',
    'database': '...',
    'charset': 'utf8'
}
```

### 실행 방법

#### 통합 시스템 실행
```bash
python integrated_system.py
```

#### 개별 모듈 테스트
```bash
# 센서 시스템만 테스트
python multi_sensor.py

# 제어 시스템만 테스트
python multi_control.py

# 모션 감지만 테스트
python motion_detector.py

# WebSocket 서버만 테스트
python websocket_server.py
```

## 🏆 주요 성과

### 농업 환경 제어 기술 적용
- 농촌진흥청 농작물 생육 기준을 제어 로직에 반영
- 시간대별 온도 관리로 일교차 제어 최적화
- 히스테리시스 제어 방식으로 장치 수명 및 안정성 향상

### 시스템 아키텍처 설계 및 안정화
- 5개 독립 스레드 기반의 병렬 구조 설계
- 실시간 측정(1분)과 데이터 저장(1시간) 주기 분리로 효율 향상
- 공유 메모리 기반 데이터 교환 구조 구현
- 안전한 리소스 정리 및 종료 처리 절차 확립

### 데이터 처리 및 성능 최적화
- 테이블 분리로 데이터 구조 효율화
- 공통 모듈화로 코드 중복 최소화
- 공유 메모리 적용으로 데이터베이스 부하 제거
- **데이터베이스 저장 횟수 99.6% 감소** (120회 → 1회)
- **DHT22 센서 안정성 30% → 거의 100%**로 개선

### 기술 통합 및 확장 역량 강화
- SPI 통신으로 아날로그 센서 데이터 처리
- asyncio 기반 비동기 WebSocket 서버 구현
- 다중 클라이언트 동시 접속 지원
- 3단계 설정 계층 구조 확립
- JSON 기반 동적 설정 관리 및 실시간 반영
- 프로그램 재시작 없이 설정 변경 가능

## 🐛 트러블슈팅

### SPI 리소스 충돌
**증상** : Device or resource busy (errno 16) 오류 발생

**원인** : multi_sensor.py와 다른 모듈에서 동시에 SPI 초기화 수행

**조치** : 
- SPI 초기화를 multi_sensor.py로 일원화
- 공용 함수(read_channel())로 참조 구조 통합

**결과** : 모듈 간 충돌 제거 및 안정적 데이터 수집 확보

**교훈** : SPI 버스는 단일 초기화 원칙을 준수해야 함

### DHT22 센서 불안정성
**증상** : 센서 데이터 10회 중 약 3~4회 읽기 실패

**원인** : 센서 물리적 제약 및 데이터시트 권장 주기 미준수

**조치** : 
- 2초 간격 최대 3회 재시도 로직 추가
- None 값 검증 강화

**결과** : 성공률 약 60~70% → 거의 100%로 개선

**교훈** : 센서 주기와 전송 조건은 데이터시트 기준에 맞춰야 함

### 데이터베이스 저장 최적화
**증상** : LED ON 상태 1시간 지속 시 120회 중복 저장 발생

**원인** : 상태 변화 여부와 관계없이 주기적 저장 수행

**조치** : 
- prev_state 기반 상태 변화 감지 로직 도입
- 변화 시에만 저장 수행

**결과** : 저장 횟수 120 → 1회로 감소 (약 99.6% 절감)

**교훈** : 상태 데이터는 이벤트 기반 저장이 효율적임

### WebSocket 서버 예외 처리
**증상** : 연결 즉시 종료 (오류 코드 1011)

**원인** : sensor_data가 None일 때 예외 미처리

**조치** : 
- None 가드 추가
- 에러 응답(status: error) 표준화

**결과** : 비정상 종료 제거, 다중 클라이언트 안정성 확보

**교훈** : 비동기 환경에서는 예외 검증과 표준 응답 구조가 필수적임

## 📊 프로젝트 통계

| 항목 | 수치 |
|------|------|
| 개발 기간 | 47일 |
| 코드 라인 | 1,530줄 |
| 파일 수 | 9개 |
| 함수 수 | 55개 |
| 스레드 | 5개 동시 실행 |
| 센서 | 4개 |
| 제어 장치 | 4개 |
| 테이블 | 2개 |
| 해결한 문제 | 30개 이상 |

## 📄 라이선스

이 프로젝트는 포트폴리오 목적으로 제작되었습니다.

**© 2025 root**