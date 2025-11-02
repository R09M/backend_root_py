# 농작물 환경 모니터링을 위한 LED, 팬 모터, 물 펌프 자동 제어 시스템
                                                                # 표준 라이브러리
import time
from datetime import datetime
                                                                # 외부 라이브러리
import RPi.GPIO as GPIO
                                                                # 로컬 모듈
from config.constant import SETTINGS
from sensor.multi_sensor import get_light_value, get_temperature, get_soil_moisture
from database.db_utils import save_control
from config.config_manager import ConfigManager

# 설정 관리자 전역 변수
config_manager = None

# 설정 관리자 초기화 함수
def init_config(manager) : 
  global config_manager
  config_manager = manager

# GPIO 핀 설정 (constant.py에서 불러오기)
LED_PIN = SETTINGS['LED_PIN']                              # LED 제어용 GPIO 핀
FAN_PIN = SETTINGS['FAN_PIN']                              # 팬 모터 제어용 GPIO 핀
PUMP_PIN = SETTINGS['PUMP_PIN']                            # 물 펌프 모터 제어용 GPIO 핀

# GPIO 초기화 설정
GPIO.setmode(GPIO.BCM)                                     # BCM 모드 사용
GPIO.setup(LED_PIN, GPIO.OUT)                              # LED 핀을 출력 모드
GPIO.setup(FAN_PIN, GPIO.OUT)                              # 팬 모터 핀을 출력 모드
GPIO.setup(PUMP_PIN, GPIO.OUT)                             # 물 펌프 핀을 출력 모드

# 제어 장비 초기화 설정 (정지) - 신호 반전이므로 HIGH가 OFF
GPIO.output(FAN_PIN, GPIO.HIGH) 
GPIO.output(PUMP_PIN, GPIO.HIGH)

# 이전 상태 추적 변수 (상태 변화 감지용)
prev_state = {
  'led': None,
  'fan': None,
  'pump': None
}

# 현재 시간을 기준으로 낮/밤 구분하는 함수
def is_daytime() :
  current_hour = datetime.now().hour
  return 6 <= current_hour < 18

# 시간대별 팬 가동 기준 온도 가져오기
def get_fan_threshold() :
  # 현재 시간대에 맞는 팬 가동 기준 온도 반환
  if is_daytime() :
    return config_manager.get_setting('fan_day')           # 낮 시간대 기준 (06:00 ~ 18:00)
  
  else :
    return config_manager.get_setting('fan_night')         # 밤 시간대 기준 (18:01 ~ 05:59)

# 조도값에 따라 LED 자동 제어
def control_led(light_value = None) :
  # 최신 조도 설정값 가져오기
  light_threshold = config_manager.get_setting('light_threshold')

  # 조도값이 제공되지 않으면 환경 센서 시스템에서 실시간 읽기
  if light_value is None :
    light_value = get_light_value()

  # 조도 설정값 기준으로 LED 제어
  if light_value < light_threshold :
    GPIO.output(LED_PIN, GPIO.HIGH)                         # 어두우면 LED 켜기
    status = "ON"
  
  else :
    GPIO.output(LED_PIN, GPIO.LOW)                          # 밝으면 LED 끄기
    status = "OFF"
  
  return {
    'device' : 'led',
    'status' : status,
    'value' : light_value
  }

# 온도에 따라 팬 모터를 자동으로 제어
def control_fan(temperature = None) :
  # 온도 데이터가 없으면 환경 센서 시스템에서 실시간 읽기
  if temperature is None :
    temperature = get_temperature()

  # 환경 데이터 읽기 실패 시 제어 건너뜀
  if temperature is None :
    return {
        'device' : 'fan',
        'status' : 'SKIPPED',
        'value' : None,
        'reason' : 'sensor_read_failed'
    }
  
  # 최신 온도 설정값 가져오기
  if is_daytime() :
    fan_threshold = config_manager.get_setting('fan_day')

  else :
    fan_threshold = config_manager.get_setting('fan_night')
    
  time_period = "낮" if is_daytime() else "밤"

  # 온도 설정값 기준으로 팬 모터 제어 판단 (반전)
  if temperature >= fan_threshold :
    GPIO.output(FAN_PIN, GPIO.LOW)                          # 팬 모터 가동
    status = "ON"

  else :
    GPIO.output(FAN_PIN, GPIO.HIGH)                         # 팬 모터 정지
    status = "OFF"

  return {
    'device' : 'fan',
    'status' : status,
    'value' : temperature,
    'threshold' : fan_threshold,
    'time_period' : time_period
  }

# 토양 수분에 따라 물 펌프 모터를 자동으로 제어 
def control_pump(soil_moisture = None) :
  # 최신 토양 수분 설정값 가져오기
  soil_min = config_manager.get_setting('soil_min')
  soil_max = config_manager.get_setting('soil_max')

  # 토양 수분 데이터가 없으면 환경 센서 시스템에서 실시간 읽기
  if soil_moisture is None :
    soil_moisture = get_soil_moisture()

  # 환경 데이터 읽기 실패 시 제어 건너뜀
  if soil_moisture is None :
    return {
      'device' : 'pump',
      'status' : 'SKIPPED',
      'value' : None,
      'reason' : 'sensor_read_failed'
    }
  
  # 토양 수분 설정값 기준으로 물 펌프 제어 판단 (반전)
  if soil_moisture < soil_min :
    # 토양 수분이 최소값보다 낮으면 물 펌프 가동
    GPIO.output(PUMP_PIN, GPIO.LOW)                          # 펌프 가동
    status = "ON"

  elif soil_moisture >= soil_max :
    # 토양 수분이 최대값에 도달하면 물 펌프 정지
    GPIO.output(PUMP_PIN, GPIO.HIGH)                         # 펌프 정지
    status = "OFF"
  
  else :
    # 설정 범위 안에 있으면 현재 상태 유지
    return {
      'device' : 'pump',
      'status' : 'maintain',
      'value' : soil_moisture,
      'reason' : 'in range'
    }

  return {
    'device' : 'pump',
    'status' : status,
    'value' : soil_moisture
  }

# 제어 상태 출력 함수
def print_control_status(device, state, mode = 'auto') :
  current_time = datetime.now().strftime('%H:%M:%S')

  mode_text = '자동 제어 상태' if mode == 'auto' else '수동 제어 상태'
  
  print("═" * 50)
  print(f"[{current_time}] {mode_text}")
  print("═" * 50)

  # device가 리스트인 경우 (여러 장치 한 번에)
  if isinstance(device, list) :
    for dev, status in device :
      print(f"{dev.upper()} : {status}")
  
  # device가 문자열인 경우 (단일 장치)
  else :
    print(f"{device.upper()} : {state}")
  
  print("═" * 50)

# 환경 센서 데이터를 기반으로 모든 제어 장비를 자동으로 제어
def control_all_devices(sensor_data = None) :
  results = {}
  state_changed = False                                   # 상태 변화 감지 플래그

  # LED 제어 (조도 기반)
  if config_manager.get_device_mode('led') == 'manual' :
    # 수동 모드
    manual_state = config_manager.get_device_state('led')
    results['led'] = {
      'device' : 'led',
      'status' : 'ON' if manual_state else 'OFF',
      'mode' : 'manual'
    }

  else :  
    # 자동 모드
    light_value = sensor_data.get('light_value') if sensor_data else None
    results['led'] = control_led(light_value)
    results['led']['mode'] = 'auto'

  # 상태 변화 확인
  if results['led']['status'] != prev_state['led'] :
    state_changed = True
    prev_state['led'] = results['led']['status']

  # 팬 모터 제어 (온도 기반)
  if config_manager.get_device_mode('fan') == 'manual':
    # 수동 모드
    manual_state = config_manager.get_device_state('fan')
    results['fan'] = {
      'device' : 'fan',
      'status' : 'ON' if manual_state else 'OFF',
      'mode' : 'manual'
    }

  else :
    # 자동 모드
    temperature =  sensor_data.get('temperature') if sensor_data else None
    results['fan'] = control_fan(temperature)
    results['fan']['mode'] = 'auto'

  # 상태 변화 확인
  if results['fan']['status'] != prev_state['fan'] :
    state_changed = True
    prev_state['fan'] = results['fan']['status']
  
  # 물 펌프 제어 (토양 수분 기반)
    if config_manager.get_device_mode('pump') == 'manual':
      # 수동 모드
      manual_state = config_manager.get_device_state('pump')
      results['pump'] = {
        'device' : 'pump',
        'status' : 'ON' if manual_state else 'OFF',
        'mode' : 'manual'
      }

  else :
    # 자동 모드
    soil_moisture = sensor_data.get('soil_moisture') if sensor_data else None
    results['pump'] = control_pump(soil_moisture)
    results['pump']['mode'] = 'auto'

  # 상태 변화 확인 (maintain 상태는 변화가 아님)
  if results['pump']['status'] != 'maintain' and results['pump']['status'] != prev_state['pump'] :
    state_changed = True
    prev_state['pump'] = results['pump']['status']

  # 제어 결과 출력
  auto_devices = []
  for device in ['led', 'fan', 'pump'] :
    if results[device].get('mode') == 'auto' and results[device]['status'] not in ['SKIPPED', 'maintain'] :
      auto_devices.append((device, results[device]['status']))

  if auto_devices:
    print_control_status(auto_devices, None, 'auto')

  # 자동 제어 시스템 데이터를 데이터베이스에 저장 (상태 변화가 있을 때만)
  if state_changed :
    save_control(
      led = 1 if results['led']['status'] == 'ON' else 0,
      fan = 1 if results['fan']['status'] == 'ON' else 0,
      pump = 1 if results['pump']['status'] == 'ON' else 0
    )

  return results

# 프로그램 종료 시 리소스 정리
def cleanup() :
  try :
    # 모든 제어 장비 OFF
    GPIO.output(LED_PIN, GPIO.LOW)                        # LED 끄기
    GPIO.output(FAN_PIN, GPIO.HIGH)                       # 팬 모터 정지 (반전)
    GPIO.output(PUMP_PIN, GPIO.HIGH)                      # 물 펌프 정지 (반전)

    # GPIO 리소스 정리
    GPIO.cleanup()                                        # 모든 GPIO 핀 리소스 해제

    print("제어 시스템 리소스 정리 완료")
      
  except Exception as e:
    print(f"리소스 정리 중 오류 발생 : {e}")

# 독립 실행 모드
if __name__ == "__main__" :
    print("═" * 50)
    print("환경 제어 시스템")
    print("═" * 50)

    # 단독 실행 시 config_manager 초기화
    init_config(ConfigManager())

    try :
      while True :
        # 모든 제어 장비 자동 제어 실행 (상태 변화 시 DB 저장)
        results = control_all_devices()

        time.sleep(30)                                     # 30초 대기 후 다시 실행

    except KeyboardInterrupt :
      print("프로그램 종료")
      
    finally :  
      cleanup()