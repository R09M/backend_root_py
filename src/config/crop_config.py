# 농작물 환경 모니터링을 위한 농작물별 설정 관리
                                                                # 로컬 모듈
from config.constant import SETTINGS

# 농작물 환경 설정
CROP_SETTINGS = {
  "strawberry" : {
    # 시간대별 온도 설정
    "temperature" : {

      # 낮 온도 범위
      "day" : {
        "min" : SETTINGS["TEMPERATURE_DAY_MIN"],             # 권장 최저 온도
        "max" : SETTINGS["TEMPERATURE_DAY_MAX"]              # 권장 최고 온도
      },

      # 밤 온도 범위
      "night" : {
        "min_safe" : SETTINGS["TEMPERATURE_NIGHT_MIN"],      # 절대 최저 온도
        "target" : SETTINGS["TEMPERATURE_NIGHT_MAX"]         # 권장 관리 온도 (10℃ 내외 유지)
      },
    },

    # 공기 습도 설정
    "humidity" : {
      "min" : SETTINGS["HUMIDITY_MIN"],                      # 권장 최저 습도
      "max" : SETTINGS["HUMIDITY_MAX"]                       # 권장 최고 습도
    },

    # 토양 수분 설정
    "soil_moisture" : {
      "min" : SETTINGS["SOIL_MOISTURE_MIN"],                 # 최저 토양 수분
      "max" : SETTINGS["SOIL_MOISTURE_MAX"]                  # 최고 토양 수분
    },

    # 조도 설정
    "illumination" : {
      "min_threshold" : SETTINGS["LIGHT_THRESHOLD"],         # 농작물 재배 최저 조도 설정값
      "led_threshold" : SETTINGS["LIGHT_THRESHOLD"]          # LED 제어 기준 조도 설정값
    },

    # 팬 모터 제어 설정
    "fan" : {
      "day_threshold" : SETTINGS["FAN_ON_DAY"],              # 낮 시간대 팬 가동 기준 온도
      "night_threshold" : SETTINGS["FAN_ON_NIGHT"]           # 밤 시간대 팬 가동 기준 온도
    }
  }
}