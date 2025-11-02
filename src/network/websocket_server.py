# 농작물 환경 모니터링을 위한 웹소켓 실시간 원격 제어 시스템
                                                                # 표준 라이브러리
import asyncio
import json
from datetime import datetime
from queue import Queue
                                                                # 외부 라이브러리
import websockets
import RPi.GPIO as GPIO
                                                                # 로컬 모듈
import sensor.multi_sensor as multi_sensor
import control.multi_control as multi_control
from config.config_manager import ConfigManager

# 웹소켓 서버 설정
WS_HOST = '0.0.0.0'                                        # 모든 네트워크 인터페이스에서 접속 허용
WS_PORT = 8765                                             # 웹소켓 포트 번호

# 전역 변수 - 통합 시스템과 공유할 데이터
sensor_data = None                                         # 센서 데이터 공유 변수
config = None                                              # 설정 관리자
clients = set()                                            # 연결된 클라이언트 목록
alert_queue = Queue()                                      # 시스템 알림 전달용

# 현재 시각 문자열 반환 (로그 출력용)
def current_time() :
  return datetime.now().strftime('%H:%M:%S')

# 타임스탬프 생성 (파일 저장용)
def datetime_stamp() :
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 공유 데이터 초기화
def init_shared_data(sensor_ref, config_ref) :
  global sensor_data, config
  sensor_data = sensor_ref
  config = config_ref

# 웹소켓 응답 JSON 생성
def make_response(command, status = 'success', **data) :
  return {
    'command' : command,
    'status' : status,
    **data
  }

# 에러 응답 전송
async def send_error(websocket, command, error) :
  response = {
    'command' : command,
    'status' : 'error',
    'message' : str(error)
  }
  
  await websocket.send(json.dumps(response, ensure_ascii = False))
  print(f"[{current_time()}] {command} 오류 : {error}")

# 모든 연결된 클라이언트에서 메시지 전송
async def broadcast(message) :
  if clients :
    # 연결이 끊긴 클라이언트 제거를 위한 리스트
    disconnected = set()

    for client in clients :
      try :
        await client.send(json.dumps(message, ensure_ascii = False))
      
      except Exception as e :
        print(f"[{current_time()}] 브로드캐스트 오류 : {e}")
        disconnected.add(client)
    
    # 끊긴 클라이언트 제거
    clients.difference_update(disconnected)

# 모든 클라이언트에게 알림 전송
async def send_alert(alert_type, message, data = None) :
  alert = {
    'command' : 'alert',
    'type' : alert_type,
    'message' : message,
    'timestamp' : datetime_stamp()
  }

  if data : 
    alert['data'] = data

  await broadcast(alert)
  print(f"[{current_time()}] 알림 전송 : {message}")

# 센서 데이터 조회 명령 처리
async def get_sensor_data(websocket) :
  try :
    # sensor_data가 None이거나 비어있는지 확인
    if sensor_data is None:
      print(f"[{current_time()}] 오류 : 센서 데이터가 초기화되지 않았습니다")
      await send_error(websocket, 'get_sensor_data', '센서 데이터가 초기화되지 않았습니다')
      return
    
    # 센서 데이터 가져오기
    temperature = sensor_data.get('temperature')
    humidity = sensor_data.get('humidity')
    soil_moisture = sensor_data.get('soil_moisture')
    light_value = sensor_data.get('light_value')
    
    # 센서 데이터 출력 (공통 함수 사용)
    if temperature is not None and humidity is not None :
      multi_sensor.print_sensor_data(
        temperature, 
        humidity, 
        soil_moisture, 
        light_value, 
        title = "실시간 원격 제어"
      )

    response = make_response(
      'get_sensor_data',
      data = {
          'temperature' : round(temperature, 1) if temperature is not None else None,
          'humidity' : round(humidity, 1) if humidity is not None else None,
          'soil_moisture' : round(soil_moisture, 1) if soil_moisture is not None else None,
          'light_value' : light_value,
          'last_update' : sensor_data.get('last_update')
      },
      created_at = datetime_stamp()
    )
    
    await websocket.send(json.dumps(response, ensure_ascii = False))
    print(f"[{current_time()}] 실시간 원격 제어 데이터 전송 완료\n")
  
  except Exception as e :
    print(f"[{current_time()}] 실시간 원격 제어 데이터 조회 오류 : {e}")
    await send_error(websocket, 'get_sensor_data', e)

# 설정값 조회 명령 처리
async def get_settings(websocket) :
  try :
    settings = config.get_all_settings()
    
    response = make_response(
      'get_settings',
      data = settings
    )
    
    await websocket.send(json.dumps(response, ensure_ascii = False))
    print(f"[{current_time()}] 설정 데이터 조회 완료\n")
  
  except Exception as e :
    print(f"[{current_time()}] 설정 데이터 조회 오류 : {e}")
    await send_error(websocket, 'get_settings', e)

# 설정값 변경 명령 처리
async def update_settings(websocket, data) :
  try :
    key = data.get('key')
    value = data.get('value')

    # 기존 값 가져오기
    old_value = config.get_setting(key)

    print(f"[{current_time()}] 설정 변경 요청 : {old_value} → {value}")

    # 설정값 업데이트
    success = config.update_setting(key, value)

    if success :
      print(f"[{current_time()}] 설정 적용 완료")

      # 설정 변경 시 해당 장치를 자동 모드로 전환
      if 'fan' in key :
        config.set_device_mode('fan', 'auto')

      elif 'light' in key or 'illum' in key :
        config.set_device_mode('led', 'auto')
        
      elif 'soil' in key :
        config.set_device_mode('pump', 'auto')

      # 설정 변경 후 즉시 제어 실행
      control_result = auto_control()

      response = make_response(
        'update_settings',
        key = key,
        new_value = value,
        control_result = control_result
      )

    else :
      await send_error(websocket, 'update_settings', '설정 저장 실패')
      return
    
    await websocket.send(json.dumps(response, ensure_ascii = False))
  
  except Exception as e :
    await send_error(websocket, 'update_settings', e)

# 수동 장치 제어 명령 처리
async def manual_control(websocket, data) :
  try :
    device = data.get('device')
    state = data.get('state')

    # 수동 모드로 변경
    state_bool = (state == 'ON')
    config.set_device_mode(device, 'manual', state_bool)

    # 즉시 제어 실행
    pin = getattr(multi_control, f'{device.upper()}_PIN')

    # 팬과 펌프는 신호 반전 (LOW = ON, HIGH = OFF)
    if device in ['fan', 'pump'] :
        GPIO.output(pin, GPIO.LOW if state == 'ON' else GPIO.HIGH)
    else:
        GPIO.output(pin, GPIO.HIGH if state == 'ON' else GPIO.LOW)
    
    # 수동 제어 출력
    multi_control.print_control_status(device, state, 'manual')
      
    response = make_response(
        'manual_control',
        device = device,
        state = state,
        mode = 'manual'
    )

    await websocket.send(json.dumps(response, ensure_ascii = False))

  except Exception as e :
      await send_error(websocket, 'manual_control', e)

# 자동/수동 모드 전환 명령 처리
async def set_mode(websocket, data) : 
  try :
    device = data.get('device')
    mode = data.get('mode')

    # 모든 장치 모드 변경
    if device == 'all' :
      success = True
      for dev in ['led', 'fan', 'pump'] :
        if not config.set_device_mode(dev, mode) :
          success = False
    
    # 개별 장치 모드 변경
    else :
      success = config.set_device_mode(device, mode)

    response = make_response(
      'set_mode',
      status = 'success' if success else 'error',
      device = device,
      mode = mode
    )

    if not success :
        response['message'] = '모드 변경 실패'
        
    await websocket.send(json.dumps(response, ensure_ascii = False))

  except Exception as e :
      await send_error(websocket, 'set_mode', e)

# 설정 변경 시 즉시 제어 실행
def auto_control() :
  global sensor_data

  try :
    # 메모리에서 최신 센서 데이터 가져오기
    current_data = {
      'temperature' : sensor_data.get('temperature'),
      'humidity' : sensor_data.get('humidity'),
      'soil_moisture' : sensor_data.get('soil_moisture'),
      'light_value' : multi_control.get_light_value()
    }

    # 제어 실행 (자동 모드인 장치만)
    results = {}

    # LED 제어 (자동 모드인 경우)
    if config.get_device_mode('led') == 'auto' :
      results['led'] = multi_control.control_led(current_data['light_value'])

    # 팬 제어 (자동 모드인 경우)
    if config.get_device_mode('fan') == 'auto' :
      results['fan'] = multi_control.control_fan(current_data['temperature'])
    
    # 펌프 제어 (자동 모드인 경우)
    if config.get_device_mode('pump') == 'auto' :
      results['pump'] = multi_control.control_pump(current_data['soil_moisture'])
    
    return results

  except Exception as e :
    print(f"[{current_time()}] 즉시 제어 오류 : {e}")
    return {'error' : str(e)}

# 시스템 알림 확인 및 전송 (대기 시간 : 0.5초)
async def alert_monitor() :
  while True :
    try :
      # 큐에 알림이 있는지 확인
      if not alert_queue.empty() :
        alert_data = alert_queue.get_nowait()
        
        # 모든 클라이언트에게 알림 전송
        await send_alert(
          alert_type = alert_data['type'],
          message = alert_data['message'],
          data = {
            'timestamp' : alert_data['timestamp']
          }
        )
      
      # 0.5초마다 체크
      await asyncio.sleep(0.5)
    
    except Exception as e :
      print(f"[{current_time()}] 알림 모니터 오류 : {e}")
      await asyncio.sleep(1)

# 클라이언트 연결 처리
async def handle_client(websocket, path) :
  # 연결된 클라이언트 목록에 추가
  clients.add(websocket)

  try :
    # 클라이언트로부터 메시지 수신 대기
    async for message in websocket :
      try :
        # JSON 형식으로 파싱
        data = json.loads(message)
        command = data.get('command')

        # 명령에 따라 처리
        if command == 'get_sensor_data' :
          await get_sensor_data(websocket)

        elif command == 'get_settings' :
          await get_settings(websocket) 
        
        elif command == 'update_settings' :
          await update_settings(websocket, data)
        
        elif command == 'manual_control' :
          await manual_control(websocket, data)

        elif command == 'set_mode' :
          await set_mode(websocket, data)
        
        else :
          await send_error(websocket, command, '알 수 없는 명령')
      
      except json.JSONDecodeError as e:
        print(f"[{current_time()}] JSON 파싱 오류 : {e}")

      except Exception as e :
        print(f"[{current_time()}] 메시지 처리 오류 : {e}")
  
  except websockets.exceptions.ConnectionClosed :
    pass

  finally :
    # 연결 종료 시 목록에서 제거
    clients.discard(websocket)

# 실시간 원격 제어 시작
async def start_server(sensor_ref, config_ref) :
  # 공유 데이터 초기화
  init_shared_data(sensor_ref, config_ref)

  # 실시간 원격 제어 서버 구동
  async with websockets.serve(handle_client, WS_HOST, WS_PORT) :
    print(f"\n[{current_time()}] 실시간 원격 제어 시작 : ws://{WS_HOST}:{WS_PORT}\n")

    # 알림 모니터 시작
    asyncio.create_task(alert_monitor())

    await asyncio.Future()                                 # 서버 계속 실행

# 독립 실행 모드
if __name__ == "__main__" :
  print("═" * 50)
  print("실시간 원격 제어 시스템")
  print("═" * 50)
  print("주의 : integrated_system.py에서 실행해야 합니다.")
  print("═" * 50)