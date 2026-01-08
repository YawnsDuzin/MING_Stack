#!/usr/bin/env python3
"""
=============================================================================
Mitsubishi MELSEC MC Protocol Simulator
MING Stack - Industrial IoT Platform
=============================================================================

MC 프로토콜 (MELSEC Communication Protocol) 시뮬레이터
- 3E 프레임 (바이너리) 지원
- 4E 프레임 (ASCII) 지원
- 디바이스 읽기/쓰기 지원

지원 디바이스:
- D: 데이터 레지스터 (Data Register)
- M: 내부 릴레이 (Internal Relay)
- X: 입력 (Input)
- Y: 출력 (Output)
- W: 링크 레지스터 (Link Register)
- R: 파일 레지스터 (File Register)

참고: 이 시뮬레이터는 개발/테스트 용도입니다.
=============================================================================
"""

import asyncio
import struct
import random
import math
import time
import os
import logging
from datetime import datetime
from typing import Dict, Tuple, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# MC 프로토콜 상수
# =============================================================================

# 서브헤더
SUBHEADER_3E_REQUEST = 0x5000  # 3E 프레임 요청
SUBHEADER_3E_RESPONSE = 0xD000  # 3E 프레임 응답

# 명령어
CMD_BATCH_READ = 0x0401   # 일괄 읽기
CMD_BATCH_WRITE = 0x1401  # 일괄 쓰기
CMD_RANDOM_READ = 0x0403  # 랜덤 읽기
CMD_RANDOM_WRITE = 0x1402 # 랜덤 쓰기

# 서브명령
SUBCMD_WORD = 0x0000  # 워드 단위
SUBCMD_BIT = 0x0001   # 비트 단위

# 디바이스 코드 (3E 프레임 바이너리)
DEVICE_CODES = {
    'D': 0xA8,   # 데이터 레지스터
    'M': 0x90,   # 내부 릴레이
    'X': 0x9C,   # 입력
    'Y': 0x9D,   # 출력
    'W': 0xB4,   # 링크 레지스터
    'R': 0xAF,   # 파일 레지스터
    'L': 0x92,   # 래치 릴레이
    'F': 0x93,   # 어나운시에이터
    'B': 0xA0,   # 링크 릴레이
    'TN': 0xC2,  # 타이머 현재값
    'CN': 0xC5,  # 카운터 현재값
}

# 디바이스 코드 역변환
DEVICE_CODES_REVERSE = {v: k for k, v in DEVICE_CODES.items()}


# =============================================================================
# MC 프로토콜 시뮬레이터
# =============================================================================

class MCProtocolSimulator:
    """Mitsubishi MELSEC MC Protocol Simulator"""

    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        self.host = host
        self.port = port
        self.start_time = time.time()

        # 디바이스 메모리 영역 초기화
        self.devices: Dict[str, Dict[int, int]] = {
            'D': {},   # 데이터 레지스터 (D0-D8191)
            'M': {},   # 내부 릴레이 (M0-M8191)
            'X': {},   # 입력 (X0-X1FF)
            'Y': {},   # 출력 (Y0-Y1FF)
            'W': {},   # 링크 레지스터 (W0-W1FF)
            'R': {},   # 파일 레지스터
            'L': {},   # 래치 릴레이
            'B': {},   # 링크 릴레이
            'TN': {},  # 타이머 현재값
            'CN': {},  # 카운터 현재값
        }

        # 시뮬레이션 데이터 초기화
        self._init_simulation_data()

    def _init_simulation_data(self):
        """시뮬레이션 초기 데이터 설정"""
        # D 레지스터 초기값
        self.devices['D'][0] = 0      # 온도 (x10)
        self.devices['D'][1] = 0      # 습도 (x10)
        self.devices['D'][2] = 0      # 압력 (x100)
        self.devices['D'][10] = 0     # 모터 속도
        self.devices['D'][20] = 0     # 생산 카운트 (하위)
        self.devices['D'][21] = 0     # 생산 카운트 (상위)
        self.devices['D'][100] = 0    # 상태 워드

        # M 릴레이 초기값
        self.devices['M'][0] = 1      # 운전 중
        self.devices['M'][1] = 0      # 알람
        self.devices['M'][2] = 1      # 안전 상태
        self.devices['M'][10] = 0     # 모터 시작 명령
        self.devices['M'][11] = 0     # 모터 정지 명령

        # X 입력 초기값
        self.devices['X'][0] = 1      # 시작 버튼
        self.devices['X'][1] = 0      # 정지 버튼
        self.devices['X'][2] = 1      # 비상정지 (NC)

        # Y 출력 초기값
        self.devices['Y'][0] = 0      # 운전 램프
        self.devices['Y'][1] = 0      # 정지 램프
        self.devices['Y'][2] = 0      # 알람 램프

        logger.info("Simulation data initialized")

    async def update_simulation(self):
        """시뮬레이션 데이터 주기적 업데이트"""
        while True:
            try:
                elapsed = time.time() - self.start_time
                running = self.devices['M'].get(0, 0) == 1

                # 온도 시뮬레이션 (25°C 기준, 30분 주기)
                temp = 25.0 + 5 * math.sin(elapsed / 1800 * 2 * math.pi)
                temp += random.gauss(0, 0.3)
                self.devices['D'][0] = int(temp * 10)  # x10 스케일

                # 습도 시뮬레이션 (60% 기준)
                humidity = 60.0 + random.gauss(0, 2)
                self.devices['D'][1] = int(humidity * 10)  # x10 스케일

                # 압력 시뮬레이션 (1.0 bar 기준)
                pressure = 1.0 + random.gauss(0, 0.02)
                self.devices['D'][2] = int(pressure * 100)  # x100 스케일

                # 모터 속도 (운전 중일 때 1500 RPM)
                if running:
                    motor_speed = 1500 + int(random.gauss(0, 20))
                else:
                    motor_speed = 0
                self.devices['D'][10] = motor_speed

                # 생산 카운트 증가 (운전 중일 때)
                if running and random.random() < 0.1:  # 10% 확률로 증가
                    count_low = self.devices['D'].get(20, 0)
                    count_high = self.devices['D'].get(21, 0)
                    count = (count_high << 16) + count_low + 1
                    self.devices['D'][20] = count & 0xFFFF
                    self.devices['D'][21] = (count >> 16) & 0xFFFF

                # 알람 조건 체크
                temp_value = self.devices['D'][0] / 10.0
                if temp_value > 35:
                    self.devices['M'][1] = 1  # 알람 ON
                    self.devices['Y'][2] = 1  # 알람 램프 ON
                else:
                    self.devices['M'][1] = 0  # 알람 OFF
                    self.devices['Y'][2] = 0  # 알람 램프 OFF

                # 출력 램프 상태
                self.devices['Y'][0] = 1 if running else 0
                self.devices['Y'][1] = 0 if running else 1

                # 상태 워드 구성
                status = 0
                status |= (1 if running else 0) << 0
                status |= (self.devices['M'].get(1, 0)) << 1
                status |= (self.devices['M'].get(2, 0)) << 2
                self.devices['D'][100] = status

                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Simulation update error: {e}")
                await asyncio.sleep(1)

    def parse_3e_request(self, data: bytes) -> Tuple[int, int, Optional[Tuple]]:
        """3E 프레임 요청 파싱"""
        if len(data) < 11:
            return 0, 0xC059, None  # 데이터 부족 에러

        try:
            # 서브헤더 (2바이트)
            subheader = struct.unpack('<H', data[0:2])[0]
            if subheader != SUBHEADER_3E_REQUEST:
                return 0, 0xC059, None

            # 네트워크 번호, PC 번호, 요청 대상 (4바이트)
            # network_no = data[2]
            # pc_no = data[3]
            # request_dest = struct.unpack('<H', data[4:6])[0]

            # 요청 데이터 길이 (2바이트)
            request_length = struct.unpack('<H', data[7:9])[0]

            # 타임아웃 (2바이트)
            # timeout = struct.unpack('<H', data[9:11])[0]

            # 명령어 (2바이트)
            command = struct.unpack('<H', data[11:13])[0]

            # 서브명령 (2바이트)
            subcommand = struct.unpack('<H', data[13:15])[0]

            return command, 0, (data[15:], subcommand)

        except Exception as e:
            logger.error(f"Parse error: {e}")
            return 0, 0xC059, None

    def handle_batch_read(self, data: bytes, subcommand: int) -> bytes:
        """일괄 읽기 처리"""
        try:
            # 디바이스 코드 (1바이트)
            device_code = data[3]

            # 선두 디바이스 번호 (3바이트, 리틀 엔디안)
            head_device = struct.unpack('<I', data[0:3] + b'\x00')[0]

            # 디바이스 점수 (2바이트)
            device_count = struct.unpack('<H', data[4:6])[0]

            # 디바이스 이름 찾기
            device_name = DEVICE_CODES_REVERSE.get(device_code, 'D')

            logger.info(f"Batch Read: {device_name}{head_device}, Count: {device_count}")

            # 데이터 읽기
            result = []
            for i in range(device_count):
                addr = head_device + i
                value = self.devices.get(device_name, {}).get(addr, 0)

                if subcommand == SUBCMD_WORD:
                    # 워드 단위 (2바이트)
                    result.extend(struct.pack('<H', value & 0xFFFF))
                else:
                    # 비트 단위 (1바이트에 1비트)
                    result.append(value & 0x01)

            return bytes(result)

        except Exception as e:
            logger.error(f"Batch read error: {e}")
            return b''

    def handle_batch_write(self, data: bytes, subcommand: int) -> bool:
        """일괄 쓰기 처리"""
        try:
            # 디바이스 코드 (1바이트)
            device_code = data[3]

            # 선두 디바이스 번호 (3바이트)
            head_device = struct.unpack('<I', data[0:3] + b'\x00')[0]

            # 디바이스 점수 (2바이트)
            device_count = struct.unpack('<H', data[4:6])[0]

            # 디바이스 이름 찾기
            device_name = DEVICE_CODES_REVERSE.get(device_code, 'D')

            logger.info(f"Batch Write: {device_name}{head_device}, Count: {device_count}")

            # 데이터 쓰기
            write_data = data[6:]
            for i in range(device_count):
                addr = head_device + i
                if subcommand == SUBCMD_WORD:
                    # 워드 단위
                    if len(write_data) >= (i + 1) * 2:
                        value = struct.unpack('<H', write_data[i*2:(i+1)*2])[0]
                        if device_name not in self.devices:
                            self.devices[device_name] = {}
                        self.devices[device_name][addr] = value
                else:
                    # 비트 단위
                    if len(write_data) > i:
                        value = write_data[i] & 0x01
                        if device_name not in self.devices:
                            self.devices[device_name] = {}
                        self.devices[device_name][addr] = value

            return True

        except Exception as e:
            logger.error(f"Batch write error: {e}")
            return False

    def build_3e_response(self, end_code: int, data: bytes = b'') -> bytes:
        """3E 프레임 응답 생성"""
        response = bytearray()

        # 서브헤더 (2바이트)
        response.extend(struct.pack('<H', SUBHEADER_3E_RESPONSE))

        # 네트워크 번호 (1바이트)
        response.append(0x00)

        # PC 번호 (1바이트)
        response.append(0xFF)

        # 요청 대상 모듈 I/O 번호 (2바이트)
        response.extend(struct.pack('<H', 0x03FF))

        # 요청 대상 모듈 국번호 (1바이트)
        response.append(0x00)

        # 응답 데이터 길이 (2바이트)
        response.extend(struct.pack('<H', 2 + len(data)))

        # 종료 코드 (2바이트)
        response.extend(struct.pack('<H', end_code))

        # 데이터
        response.extend(data)

        return bytes(response)

    async def handle_client(self, reader: asyncio.StreamReader,
                           writer: asyncio.StreamWriter):
        """클라이언트 연결 처리"""
        addr = writer.get_extra_info('peername')
        logger.info(f"Client connected: {addr}")

        try:
            while True:
                # 데이터 수신
                data = await reader.read(1024)
                if not data:
                    break

                logger.debug(f"Received: {data.hex()}")

                # 요청 파싱
                command, error_code, parsed = self.parse_3e_request(data)

                if error_code != 0:
                    # 에러 응답
                    response = self.build_3e_response(error_code)
                elif command == CMD_BATCH_READ:
                    # 일괄 읽기
                    read_data, subcommand = parsed
                    result = self.handle_batch_read(read_data, subcommand)
                    response = self.build_3e_response(0, result)
                elif command == CMD_BATCH_WRITE:
                    # 일괄 쓰기
                    write_data, subcommand = parsed
                    success = self.handle_batch_write(write_data, subcommand)
                    response = self.build_3e_response(0 if success else 0xC059)
                else:
                    # 지원하지 않는 명령
                    logger.warning(f"Unsupported command: 0x{command:04X}")
                    response = self.build_3e_response(0xC059)

                # 응답 전송
                writer.write(response)
                await writer.drain()
                logger.debug(f"Sent: {response.hex()}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Client handler error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"Client disconnected: {addr}")

    async def start(self):
        """서버 시작"""
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )

        addr = server.sockets[0].getsockname()
        logger.info(f"MC Protocol Simulator started on {addr[0]}:{addr[1]}")
        logger.info("Supported devices: D, M, X, Y, W, R")

        # 시뮬레이션 업데이트 태스크 시작
        simulation_task = asyncio.create_task(self.update_simulation())

        try:
            async with server:
                await server.serve_forever()
        finally:
            simulation_task.cancel()


# =============================================================================
# 메인
# =============================================================================

async def main():
    """메인 함수"""
    port = int(os.environ.get('MC_PORT', '5000'))
    host = os.environ.get('MC_HOST', '0.0.0.0')

    print("=" * 60)
    print("  Mitsubishi MELSEC MC Protocol Simulator")
    print("  MING Stack - Industrial IoT Platform")
    print("=" * 60)
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Protocol: MC Protocol 3E Frame (Binary)")
    print("=" * 60)
    print()
    print("Simulated Devices:")
    print("  D0    : Temperature (x10)")
    print("  D1    : Humidity (x10)")
    print("  D2    : Pressure (x100)")
    print("  D10   : Motor Speed (RPM)")
    print("  D20-21: Production Count (32-bit)")
    print("  D100  : Status Word")
    print("  M0    : Running (R/W)")
    print("  M1    : Alarm (R)")
    print("  M10   : Motor Start Command (W)")
    print("  M11   : Motor Stop Command (W)")
    print()

    simulator = MCProtocolSimulator(host=host, port=port)
    await simulator.start()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Simulator stopped by user")
