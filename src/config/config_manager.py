# 농작물 환경 모니터링을 위한 사용자 설정 관리 시스템
                                                                # 표준 라이브러리
import json
import os
from datetime import datetime
                                                                # 로컬 모듈
from config.constant import SETTINGS

# 설정 파일 경로
CONFIG_FILE = 'user_settings.json'

# 타임스탬프 생성 (파일 저장용)
def datetime_stamp():
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 설정 관리 클래스 - JSON 파일로 사용자 설정을 영구 보관하고 관리
class ConfigManager :
  def __init__(self) :
    self.settings = None                                       # 설정 데이터를 저장하는 변수
    self.load_settings()                                       # 설정 파일 로드
  
  # 사용자 설정 데이터 불러오기
  def load_settings(self) : 
    try : 
      # 설정 파일 존재 여부 확인
      if os.path.exists(CONFIG_FILE) :
        with open(CONFIG_FILE, 'r', encoding = 'utf-8') as f :
          self.settings = json.load(f)
      
      else :
        self._create_defaults()
    
    except Exception as e :
      print(f"사용자 설정 관리 시스템 로드 오류 : {e}")
      self._create_defaults()
  
  # constant.py의 기본 설정 데이터 생성
  def _create_defaults(self) :
    self.settings = {
      # 시스템 설정값 (constant.py 기본값으로 초기화)
      'system_settings' : {
        'light_threshold' : SETTINGS['LIGHT_THRESHOLD'],
        'temp_day_min' : SETTINGS['TEMPERATURE_DAY_MIN'],
        'temp_day_max' : SETTINGS['TEMPERATURE_DAY_MAX'],
        'temp_night_min' : SETTINGS['TEMPERATURE_NIGHT_MIN'],
        'temp_night_max' : SETTINGS['TEMPERATURE_NIGHT_MAX'],
        'humidity_min' : SETTINGS['HUMIDITY_MIN'],
        'humidity_max' : SETTINGS['HUMIDITY_MAX'],
        'soil_min' : SETTINGS['SOIL_MOISTURE_MIN'],
        'soil_max' : SETTINGS['SOIL_MOISTURE_MAX'],
        'fan_day' : SETTINGS['FAN_ON_DAY'],
        'fan_night' : SETTINGS['FAN_ON_NIGHT']
      },

      # 장치별 제어 모드
      'device_modes' : {
        'led' : 'auto',
        'fan' : 'auto',
        'pump' : 'auto'
      },

      # 수동 제어 시 장치 상태
      'manual_states' : {
        'led' : False,
        'fan' : False,
        'pump' : False
      },

      # 메타 정보
      'created_at' : datetime_stamp(),
      'last_modified': datetime_stamp()
    }

    # 파일로 저장
    self.save_settings()
  
  # 설정 데이터 저장
  def save_settings(self) :
    try :
      # 마지막 수정 시간 업데이트
      self.settings['last_modified'] = datetime_stamp()

      # JSON 파일로 저장 (들여쓰기 적용, 한글 유지)
      with open(CONFIG_FILE, 'w', encoding = 'utf-8') as f :
        json.dump(self.settings, f, indent = 2, ensure_ascii = False)

      return True
    
    except Exception as e :
      print(f"사용자 설정 관리 시스템 저장 오류 : {e}")
      return False
  
  # 특정 설정값 가져오기
  def get_setting(self, key) :
    return self.settings['system_settings'].get(key)
  
  # 설정값 변경 및 저장
  def update_setting(self, key, value) :
    self.settings['system_settings'][key] = value
    return self.save_settings()
  
  # 장치 제어 모드 가져오기
  def get_device_mode(self, device) :
    return self.settings['device_modes'].get(device, 'auto')
    
  # 장치 제어 모드 및 상태 변경
  def set_device_mode(self, device, mode, state = None) :
    self.settings['device_modes'][device] = mode

    if mode == 'manual' and state is not None :
      self.settings['manual_states'][device] = state
    
    return self.save_settings()
    
  # 수동 모드 시 장치 상태 가져오기
  def get_device_state(self, device) :
    return self.settings['manual_states'].get(device, False)
    
  # 모든 설정 가져오기
  def get_all_settings(self) :
    return self.settings
  
  # 모든 설정 초기화
  def reset(self) :
      self._create_defaults()
      return True

# 독립 실행 모드
if __name__ == "__main__" :
  print("═" * 50)
  print("사용자 설정 관리 시스템")
  print("═" * 50)

  config = ConfigManager()
  settings = config.get_all_settings()
  
  print("\n[시스템 설정값]")
  rs = settings['system_settings']
  print(f"낮 온도 : {rs['temp_day_min']} ~ {rs['temp_day_max']}℃")
  print(f"밤 온도 : {rs['temp_night_min']} ~ {rs['temp_night_max']}℃")
  print(f"습도 : {rs['humidity_min']} ~ {rs['humidity_max']}%")
  print(f"토양 : {rs['soil_min']} ~ {rs['soil_max']}%")
  print(f"조도 : {rs['light_threshold']}")
  
  print("\n[시스템 모드]")
  dm = settings['device_modes']
  print(f"LED : {dm['led']}")
  print(f"팬 : {dm['fan']}")
  print(f"펌프 : {dm['pump']}")