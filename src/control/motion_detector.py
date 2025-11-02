# 농작물 환경 모니터링을 위한 모션 센서 및 부저 알람 시스템
                                                                # 표준 라이브러리
import time
from datetime import datetime
                                                                # 외부 라이브러리
import RPi.GPIO as GPIO
                                                                # 로컬 모듈
from config.constant import SETTINGS
from database.db_utils import save_control

# GPIO 핀 설정 (constant.py에서 불러오기)
PIR_PIN = SETTINGS['PIR_PIN']                              # PIR 모션 센서용 GPIO 핀
BUZZER_PIN = SETTINGS['BUZZER_PIN']                        # 부저용 GPIO 핀

# 알람 설정 (constant.py에서 불러오기)
ALARM_FREQ = SETTINGS['ALARM_FREQ']                        # 알람 주파수 (Hz) [낮은음, 높은음]
ALARM_REPEAT = SETTINGS['ALARM_REPEAT']                    # 알람 반복 횟수

# GPIO 초기화 설정
GPIO.setwarnings(False)                                    # GPIO 경고 메시지 비활성화
GPIO.setmode(GPIO.BCM)                                     # BCM 모드 사용 (다른 모듈과 통일)

# PIR 센서 및 부저 핀 설정
GPIO.setup(PIR_PIN, GPIO.IN)                               # PIR 센서 핀을 입력 모드
GPIO.setup(BUZZER_PIN, GPIO.OUT)                           # 부저 핀을 출력 모드

# 부저 PWM 객체 설정
buzzer = GPIO.PWM(BUZZER_PIN, 1000)                        # 1000Hz로 PWM 객체 생성

# 부저 기본 동작 테스트
def test_buzzer() :
  print("부저 테스트 중...")
  GPIO.output(BUZZER_PIN, GPIO.HIGH)
  time.sleep(1)

  GPIO.output(BUZZER_PIN, GPIO.LOW)
  print("부저 테스트 완료")

# 알람 소리 재생 (삐용삐용 패턴의 사이렌 소리)
def control_buzzer() :
  try :
    # 설정된 횟수만큼 알람 패턴 반복
    for repeat in range(ALARM_REPEAT) :
      # 각 주파수별로 소리 재생 (낮은음 → 높은음)
      for freq in ALARM_FREQ :
        buzzer.ChangeFrequency(freq)                       # PWM 주파수 변경
        buzzer.start(50)                                   # 50% 듀티 사이클로 시작
        time.sleep(0.3)                                    # 0.3초 동안 해당 주파수 재생

      buzzer.stop()                                        # 각 패턴 완료 후 잠시 정지
      time.sleep(0.1)                                      # 0.1초 무음 구간

    return {
      'device' : 'buzzer',
      'status' : 'completed',
      'value' : True
    }
  
  except Exception as e :
    print(f"부저 제어 오류 : {e}")

    return {
      'device' : 'buzzer',
      'status' : 'error',
      'value' : False,
      'reason' : str(e)
    }

# 모션 감지 및 알람 실행
def detect_motion() :
  try :
    # PIR 센서에서 디지털 신호 읽기 (0 또는 1)
    motion_detected = GPIO.input(PIR_PIN)
    
    # 움직임이 감지된 경우
    if motion_detected == 1 :
      print("\n" + "═" * 50)
      print("[모션 감지]")
      print("═" * 50)
      current_time = datetime.now().strftime('%H:%M:%S')
      print(f"[{current_time}] 움직임 감지!")
      buzzer_result = control_buzzer()

      # 모션 감지 시 위험 레벨 알림으로 데이터베이스에 저장
      save_control(motion = 1)

      return {
        'device' : 'motion_sensor',
        'status' : 'detected',                             # 감지됨
        'value' : True,
        'buzzer_result' : buzzer_result
      }
    
    # 움직임이 감지되지 않은 경우 (평상시)
    else :
      return {
        'device' : 'motion_sensor',
        'status' : 'none',                                 # 감지 안됨
        'value' : False
      }

  except Exception as e :
    print(f"모션 센서 오류 : {e}")

    return {
      'device' : 'motion_sensor',
      'status' : 'error',
      'value' : False,
      'reason' : str(e)                                    # 디버깅용 오류 메시지
    }

# 프로그램 종료 시 리소스 정리
def cleanup() :
  try :
    buzzer.stop()                                          # PWM 객체 중지
    GPIO.cleanup()                                         # 모든 GPIO 핀 리소스 해제
    print("모션 감지 시스템 리소스 정리 완료")

  except Exception as e :
    print(f"리소스 정리 중 오류 발생 : {e}")

# 독립 실행 모드
if __name__ == "__main__" :
  print("═" * 50)
  print("모션 감지 시스템")
  print("═" * 50)

  # 시스템 초기화 및 테스트
  test_buzzer()                                            # 부저 동작 확인

  # PIR 센서 안정화 대기
  print("센서 안정화 중... (5초 대기)\n")
  time.sleep(5)
  print("모션 모니터링 시작")

  try :
    while True :
      motion_result = detect_motion()

      # 움직임이 감지된 경우
      if motion_result['status'] == 'detected' :
        time.sleep(5)                                      # 알람 완료 후 5초 대기 (연속 감지 방지)
      
      # 센서 오류 발생 시
      elif motion_result['status'] == 'error' :
        time.sleep(1)                                      # 1초 대기 후 재시도
      
      # 평상시 (움직임 없음)
      else :
        time.sleep(1)                                      # 1초 대기 후 다시 감지 시도

  except KeyboardInterrupt:
    print("프로그램 종료")
  
  finally :
    cleanup()