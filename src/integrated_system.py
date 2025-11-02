# 농작물 환경 모니터링을 위한 통합 센서 및 자동 제어 시스템
                                                                # 표준 라이브러리
import time
import threading
from datetime import datetime
import signal
import sys
import asyncio
                                                               # 로컬 모듈
import sensor.multi_sensor as multi_sensor
import control.multi_control as multi_control
import control.motion_detector as motion_detector
import network.websocket_server as websocket_server
from config.constant import SETTINGS 
from config.config_manager import ConfigManager

# 통합 농작물 환경 모니터링 시스템 - 모든 센서와 자동 제어 장비를 동시에 관리하는 클래스
class IntegratedSystem:
    def __init__(self):
        # 시스템 동작 상태를 저장하는 변수
        self.running = False                                   # 시스템 실행 상태 플래그
        self.threads = []                                      # 멀티스레드 작업 목록
        
        # 공유 센서 데이터 (모든 스레드가 접근 가능한 메모리)
        self.shared_sensor_data = {
            'temperature': None,                               # 온도 (℃)
            'humidity': None,                                  # 습도 (%)
            'soil_moisture': None,                             # 토양 수분 (%)
            'light_value': None,                               # 조도 (0 ~ 1023)
            'last_update': None                                # 마지막 업데이트 시간
        }

        # 설정 관리자 초기화
        self.config_manager = ConfigManager()

        # 설정 관리자를 제어 시스템에 전달
        multi_control.init_config(self.config_manager)

        # 시스템 안전 종료용
        signal.signal(signal.SIGINT, self.stop_system)

    # 시스템 안전 종료 및 리소스 정리
    def stop_system(self, sig = None, frame = None) :
        print("시스템 종료 중...")
        self.running = False

        # 모든 하드웨어 모듈의 리소스 정리
        try :
            multi_sensor.cleanup()                             # 센서 모듈 정리 (SPI 연결 해제)
        except Exception as e :
            print(f"센서 모듈 정리 중 오류 : {e}")
            pass
        
        try :
            multi_control.cleanup()                            # 모션 감지 모듈 정리 (GPIO 해제)
        except Exception as e :
            print(f"제어 모듈 정리 중 오류 : {e}")
            pass
        
        try :
            motion_detector.cleanup()                          # 모션 감지 모듈 정리 (GPIO 해제)
        except Exception as e :
            print(f"모션 감지 모듈 정리 중 오류 : {e}")
            pass
        
        print("시스템 종료 완료")
        sys.exit(0)

    # 환경 센서 데이터 수집 및 데이터베이스 저장 작업 스레드 (대기 시간 : 1시간)
    def sensor_data_worker(self) :
        while self.running :
            try :
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"\n[{current_time}] 환경 센서 데이터 수집 시작")

                sensor_data = multi_sensor.read_all_sensors()
                
                if sensor_data and sensor_data.get('status') == 'success' :
                    print(f"다음 수집까지 {SETTINGS['SAVE_INTERVAL']//60}분 대기\n")
                    time.sleep(SETTINGS['SAVE_INTERVAL'])

                else :
                    print("데이터 수집 실패 - 1분 후 재시도\n")
                    time.sleep(60)                               # 1분 대기 후 재시도

            except Exception as e :
                print(f"환경 센서 시스템 스레드 오류 : {e}")
                time.sleep(2)

    # 환경 센서 데이터 실시간 체크 작업 스레드 (대기 시간 : 1분)
    def sensor_read_worker(self) :
        while self.running :
            try :
                # DHT22 온습도 센서 읽기 (재시도 로직)
                temperature, humidity, error = multi_sensor.read_dht22()

                # 센서 오류 발생 시 알림 전송
                if error :
                    websocket_server.alert_queue.put({
                        'type': 'sensor_error',
                        'message': error,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                # 토양 수분 센서 읽기
                soil_value = multi_sensor.read_channel(multi_sensor.SOIL_CHANNEL)
                soil_percent = multi_sensor.convert_to_percent(soil_value)
                
                # 조도 센서 읽기
                light_value = multi_sensor.read_channel(multi_sensor.LIGHT_CHANNEL)
                
                # 공유 메모리에 센서 데이터 저장
                if temperature is not None and humidity is not None :
                    self.shared_sensor_data.update({
                        'temperature' : temperature,
                        'humidity' : humidity,
                        'soil_moisture' : soil_percent,
                        'light_value' : light_value,
                        'last_update' : datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                    # 공유 센서 데이터 출력
                    multi_sensor.print_sensor_data(temperature, humidity, soil_percent, light_value, title = "공유 센서 데이터")

                time.sleep(SETTINGS['READ_INTERVAL'])
            
            except Exception as e :
                print(f"환경 센서 데이터 실시간 체크 스레드 오류 : {e}")
                time.sleep(2)

    # 자동 제어 시스템 작업 스레드 (대기 시간 : 5분)
    def control_worker(self) :
        multi_control.init_config(self.config_manager)

        while self.running :
            try :
                sensor_data = {
                    'temperature' : self.shared_sensor_data['temperature'],
                    'humidity' : self.shared_sensor_data['humidity'],
                    'soil_moisture' : self.shared_sensor_data['soil_moisture'],
                    'light_value' : multi_control.get_light_value()
                }

                # 모든 제어 장비 동작 및 상태 데이터베이스 저장
                results = multi_control.control_all_devices(sensor_data)

                time.sleep(SETTINGS['CONTROL_INTERVAL'])        # 5분 대기 후 재시도

            except Exception as e :
                print(f"제어 시스템 스레드 오류 : {e}")
                time.sleep(10)

    # 모션 감지 및 알람 작업 스레드 (대기 시간 : 1초)
    def motion_worker(self) :
        # PIR 센서 모션 감지 및 부저 알람
        while self.running :
            try :
                motion_result = motion_detector.detect_motion()

                if motion_result['status'] == 'detected' :
                    # 시스템 알림에 모션 감지 데이터 추가
                    websocket_server.alert_queue.put({
                        'type' : 'motion',
                        'message' : '모션이 감지되었습니다.',
                        'timestamp' : datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

                    time.sleep(5)                                   # 알람 완료 후 5초 대기
                
                elif motion_result['status'] == 'error' :
                    time.sleep(2)                                   # 오류 시 2초 후 재시도

                else :
                    time.sleep(1)                                   # 평상시 1초마다 모션 체크

            except Exception as e:
                print(f"모션 감지 스레드 오류 : {e}")
                time.sleep(2)

    # 실시간 원격 제어 작업 스레드
    def websocket_worker(self) :
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try :
            # 실시간 원격 제어 서버 시작
            loop.run_until_complete(
                websocket_server.start_server(
                    self.shared_sensor_data,                        # 센서 데이터 공유
                    self.config_manager,                            # 설정 관리자 공유
                )
            )
        
        except Exception as e :
            print(f"실시간 원격 제어 스레드 오류 : {e}")
        
        finally :
            loop.close()

    # 모든 센서 및 제어 시스템 멀티스레드 작업 시작
    def start_all(self) :
        print("통합 모니터링 시스템 시작")

        self.running = True                                         # 작업 시작 신호

        # 각각의 작업을 담당하는 스레드 생성
        self.threads = [
            threading.Thread(
                target = self.sensor_data_worker,
                name = "환경 센서 데이터 수집",
                daemon = True                                       # 메인 프로그램 종료 시 같이 종료
            ),
            threading.Thread(
                target = self.sensor_read_worker,
                name = "환경 센서 데이터 실시간 체크",
                daemon = True
            ),
            threading.Thread(
                target = self.control_worker,
                name = "자동 제어 시스템",
                daemon = True
            ),
            threading.Thread(
                target = self.motion_worker,
                name = "모션 감지 알람",
                daemon = True
            ),
            threading.Thread(
                target = self.websocket_worker,
                name = "실시간 원격 제어",
                daemon = True
            )
        ]
        
        # 모든 작업 스레드 동시에 시작
        for thread in self.threads :
            thread.start()                                          # 작업 시작
            print(f"- {thread.name}", flush = True)

# 통합 시스템 메인 실행 함수
def main() :
    # 시스템 객체 생성 및 초기화
    system = IntegratedSystem()

    try :
        system.start_all()                                          # 모든 센서 작업 스레드 시작

        # 상태 체크 루프 (시스템이 잘 돌아가는지 15초마다 확인)
        start_time = datetime.now()
        while True :
            time.sleep(15)                                          # 15초 대기

            # 현재 시간 및 실행 시간 계산
            elapsed = datetime.now() - start_time
            current_time = datetime.now().strftime('%H:%M:%S')
            hours = elapsed.seconds // 3600
            minutes = (elapsed.seconds % 3600) // 60
            seconds = elapsed.seconds % 60

            # 실행 시간을 읽기 쉽게 변환
            if hours > 0 :
                runtime = f"{hours}시간 {minutes}분 {seconds}초"
            elif minutes > 0 :
                runtime = f"{minutes}분 {seconds}초"
            else :
                runtime = f"{seconds}초"

            print(f"[{current_time}] 농작물 환경 모니터링 시스템 정상 작동 중 (실행시간 : {runtime})")

    except Exception as e :
        print(f"시스템 오류 : {e}")
        system.stop_system()

if __name__ == "__main__":
    print("═" * 50)
    print("농작물 환경 모니터링 통합 시스템")
    print("═" * 50)
    
    main()                                                             # 메인 함수 실행