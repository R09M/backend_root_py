# 농작물 환경 모니터링을 위한 데이터베이스 유틸리티
                                                                # 외부 라이브러리
import pymysql
from datetime import datetime
                                                                # 로컬 모듈
from config.constant import DATABASE_CONFIG

# 환경 센서 데이터를 GROWING_ENVIRONMENT 테이블에 저장
def save_sensor(temperature, humidity, soil_percent, light_value) :
    try :
      db = pymysql.connect(**DATABASE_CONFIG)
      cursor = db.cursor()
  
      # GROWING_ENVIRONMENT 테이블에 데이터 삽입
      sql = f"""
      INSERT INTO GROWING_ENVIRONMENT (
          TEMPER
          , HUMIDITY
          , SOIL_HUMIDITY
          , ILLUMINATION
      ) VALUES (
          {temperature:.1f},
          {humidity:.1f},
          {soil_percent:.1f},
          {light_value}
      )
      """

      # 쿼리 실행 및 데이터베이스에 반영
      cursor.execute(sql)
      db.commit()
      db.close()

      current_time = datetime.now().strftime('%H:%M:%S')
      print(f"[{current_time}] 환경 센서 데이터 저장 완료")
      return True
        
    except Exception as e :
      print(f"환경 센서 데이터 저장 오류 : {e}")
      return False

# 자동 제어 시스템 데이터를 DEVICE_STATUS 테이블에 저장
def save_control(motion = 0, fan = 0, pump = 0, led = 0) :
  try :
    db = pymysql.connect(**DATABASE_CONFIG)
    cursor = db.cursor()

    # DEVICE_STATUS 테이블에 데이터 삽입
    sql = f"""
    INSERT INTO DEVICE_STATUS(
      MOTION_DETECTED
      , FAN_MOTOR
      , WATER_PUMP
      , LED_LIGHT
    ) VALUES(
      {motion}
      , {fan}
      , {pump}
      , {led}
    )
    """

    # 쿼리 실행 및 데이터베이스에 반영
    cursor.execute(sql)
    db.commit()
    db.close()

    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] 제어 시스템 데이터 저장 완료")
    return True
  
  except Exception as e :
    print(f"제어 시스템 데이터 저장 오류 : {e}")
    return False