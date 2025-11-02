# 농작물 환경 모니터링을 위한 온습도, 토양 수분, 조도 센서 시스템
                                                                # 표준 라이브러리
import time
                                                                # 외부 라이브러리
import board
import adafruit_dht
import spidev
                                                                # 로컬 모듈
from config.constant import SETTINGS
from config.crop_config import CROP_SETTINGS
from database.db_utils import save_sensor

# 농작물 설정값 가져오기
config = CROP_SETTINGS['strawberry']

# DHT22 온습도 센서 초기화
DHT22_PIN = SETTINGS['DHT22_PIN']                      # GPIO 14번 핀
dht_sensor = adafruit_dht.DHT22(getattr(board, f"D{DHT22_PIN}")) 

# MCP3008 ADC 통신 설정 (토양 수분, 조도센서 아날로그 값 읽기용)
spi = spidev.SpiDev()
spi.open(0, 0)                                         # SPI 채널 0, 디바이스 0 (CE0 핀)
spi.max_speed_hz = 1000000                             # SPI 통신 속도 : 1MHz

# 센서별 하드웨어 채널 및 핀 설정
SOIL_CHANNEL = SETTINGS['SOIL_CHANNEL']                # FC-28 토양 수분 센서 MCP3008 채널
LIGHT_CHANNEL = SETTINGS['LIGHT_CHANNEL']              # LDR 조도센서 MCP3008 채널

# MCP3008 ADC에서 아날로그 값 읽기 (0 ~ 1023 범위)
def read_channel(channel) :
    try :
        # MCP3008 SPI 통신 프로토콜
        val = spi.xfer2([1, (8 + channel) << 4, 0])
        # 10비트 ADC 값 추출 (상위 2비트 + 하위 8비트 조합)
        data = ((val[1] & 3) << 8) + val[2]
        return data

    except Exception as e :
        print(f"ADC 채널 {channel} 읽기 오류 : {e}")
        return 0

# 토양 수분 퍼센트로 변환 (0 ~ 100%)
def convert_to_percent(value) :
    try :
        return 100.0 - round(((value * 100) / 1023), 1)
    
    except Exception as e :
        print(f"토양 수분 퍼센트 변환 오류 : {e}")
        return 0.0
    
# DHT22 센서 재시도 로직
def read_dht22(retry_delay = 2, max_attempts = 3) :
    for attempt in range(max_attempts) :
        try :
            # DHT22 온습도 센서 읽기
            temperature = dht_sensor.temperature
            humidity = dht_sensor.humidity

            # 센서 읽기 성공 여부 확인
            if temperature is None or humidity is None :
                print(f"DHT22 센서 읽기 실패 - {retry_delay}초 후 재시도 ({attempt + 1}/{max_attempts})")
                if attempt < 2 :
                    time.sleep(retry_delay)

            else :
                print("DHT22 센서 읽기 성공")
                return temperature, humidity, None     # 성공 시 루프 탈출

        except Exception as e :
            print(f"DHT22 센서 오류 : {e} - {retry_delay}초 후 재시도 ({attempt + 1}/{max_attempts})")
            if attempt < max_attempts - 1 :
                time.sleep(retry_delay)
    
    return None, None, "DHT22 센서 데이터 수신 실패"        # 모든 재시도 실패 시 None 반환

# 환경 센서 데이터 출력 공통 함수
def print_sensor_data(temperature, humidity, soil_moisture, light_value, title = "환경 센서 데이터") :
    # 수집된 센서 데이터 결과값 출력
    print("\n" + "═" * 50)
    print(f"[{title}]")
    print("═" * 50)

    print(f"온도 : {temperature:.1f}°C")
    print(f"습도 : {humidity:.1f}%")
    print(f"토양 : {soil_moisture:.1f}%")
    print(f"조도 : {light_value}")

    print("═" * 50)
    
# 모든 환경 센서 데이터를 수집하고 데이터베이스에 저장하는 메인 함수
def read_all_sensors() :
    # DHT22 온습도 센서 읽기 (재시도 로직 적용)
    temperature, humidity, error = read_dht22()

    # FC-28 토양 수분 센서 읽기
    soil_value = read_channel(SOIL_CHANNEL)
    soil_percent = convert_to_percent(soil_value)

    # LDR 조도 센서 읽기
    light_value  = read_channel(LIGHT_CHANNEL)

    # 수집된 센서 데이터 결과값 출력 (성공 시에만)
    if temperature is not None and humidity is not None :
        print_sensor_data(temperature, humidity, soil_percent, light_value)

    # 환경 센서 데이터를 데이터베이스 저장
    success = save_sensor(temperature, humidity, soil_percent, light_value)

    # 수집된 데이터와 처리 상태를 딕셔너리로 반환
    return {
        'temperature': temperature,
        'humidity': humidity,
        'soil_moisture': soil_percent,
        'light_value': light_value,
        'status': 'success' if success else 'db_error',
        'error' : error
    }

# 외부 모듈에서 조도값을 요청할 때 사용하는 함수
def get_light_value() :
    return read_channel(LIGHT_CHANNEL)

# 외부 모듈에서 온도값을 요청할 때 사용하는 함수
def get_temperature() :
    temperature, _, error = read_dht22()
    return temperature, error

# 외부 모듈에서 토양 수분값을 요청할 때 사용하는 함수
def get_soil_moisture():
    soil_value = read_channel(SOIL_CHANNEL)
    return convert_to_percent(soil_value)

# 프로그램 종료시 리소스 정리
def cleanup() :
    try :
        spi.close()                                     # SPI 연결 종료
        print("리소스 정리 완료")

    except Exception as e :
        print(f"리소스 정리 중 오류 : {e}")

# 독립 실행 모드
if __name__ == "__main__" :
    print("═" * 50)
    print(f"환경 센서 모니터링 시스템 ({SETTINGS['SAVE_INTERVAL']//60}분)")
    print("═" * 50)
    
    try :
        while True :
            # 모든 센서 데이터 수집 및 저장
            result = read_all_sensors()
            
            # 처리 결과에 따른 상태 메세지 출력
            if result['status'] != 'success' :
                print("데이터 저장 실패")
            
            # 다음 데이터 수집까지 대기
            print(f"다음 측정까지 {SETTINGS['SAVE_INTERVAL']//60}분 대기\n")
            time.sleep(SETTINGS['SAVE_INTERVAL'])
            
    except KeyboardInterrupt :
        cleanup()
        print("프로그램 종료")