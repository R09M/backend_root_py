# 농작물 환경 모니터링 시스템 설정 관리

SETTINGS = {
  # 시간대별 온도 설정
  'TEMPERATURE_DAY_MIN' : 17,              # 낮 시간대 최적 하한 온도
  'TEMPERATURE_DAY_MAX' : 20,              # 낮 시간대 최적 상한 온도
  'TEMPERATURE_NIGHT_MIN' : 8,             # 밤 시간대 최적 하한 온도
  'TEMPERATURE_NIGHT_MAX' : 10,            # 밤 시간대 최적 상한 온도 (10℃ 내외)

  # 공기 습도 설정
  'HUMIDITY_MIN' : 50,                     # 공기 습도 최저 설정값
  'HUMIDITY_MAX' : 70,                     # 공기 습도 최고 설정값

  # 토양 수분 설정
  'SOIL_MOISTURE_MIN' : 60,                # 토양 수분 최저 설정값
  'SOIL_MOISTURE_MAX' : 75,                # 토양 수분 최고 설정값

  # 데이터 수집 관련 시간 설정
  'SAVE_INTERVAL': 3600,                   # 환경 데이터 저장 주기 (초) - 1시간
  'READ_INTERVAL': 60,                     # 환경 데이터 체크 주기 (초) - 1분
  'CONTROL_INTERVAL' : 300,                # 제어 시스템 체크 주기 (초) - 5분

  # MCP3008 ADC 채널 설정
  'SOIL_CHANNEL': 0,                       # FC-28 토양 수분 센서 MCP3008 채널
  'LIGHT_CHANNEL': 1,                      # LDR 조도 센서 MCP3008 채널

  # 온습도 센서 핀 설정
  'DHT22_PIN': 14,                         # DHT22 온습도 센서용 GPIO 핀

  # LED 제어 핀 설정
  'LED_PIN': 2,                            # LED 제어용 GPIO 핀

  # 팬 모터 핀 설정
  'FAN_PIN': 27,                           # 팬 모터 제어용 GPIO 핀

  # 물 펌프 핀 설정
  'PUMP_PIN' : 5,                          # 물 펌프 모터 제어용 GPIO 핀

  # 모션 센서 및 부저 핀 설정
  'PIR_PIN' : 17,                          # PIR 모션 센서용 GPIO 핀
  'BUZZER_PIN' : 3,                        # 부저용 GPIO 핀

  # 센서 제어 설정
  'LIGHT_THRESHOLD' : 400,                 # 조도 설정값
  'FAN_ON_DAY' : 20,                       # 낮 시간대 팬 가동 기준 온도
  'FAN_ON_NIGHT' : 10,                     # 밤 시간대 팬 가동 기준 온도

  'ALARM_FREQ' : [262, 330],               # 알람 주파수 (Hz)
  'ALARM_REPEAT' : 5,                      # 알람 반복 횟수
}

# 데이터베이스 연결 설정
DATABASE_CONFIG = {
  'host': '...',                           # 데이터베이스 서버 주소
  'user': '...',                           # 데이터베이스 사용자명
  'password': '...',                       # 데이터베이스 비밀번호
  'database': '...',                       # 데이터베이스명
  'charset': 'utf8'                        # 데이터베이스 문자 인코딩 (UTF-8, 한글 지원)
}