#!/usr/bin/env python3
"""
Siemens S7 PLC Simulator for MING Stack
S7 통신 프로토콜 시뮬레이션 (Snap7 라이브러리 기반)

데이터 블록 구조 (DB1):
Offset  Type    Name            Description
------  ----    ----            -----------
0       REAL    Temperature     온도 (°C)
4       REAL    Humidity        습도 (%)
8       REAL    Pressure        압력 (bar)
12      INT     MotorSpeed      모터 속도 (RPM)
14      DINT    ProductCount    생산 카운트
18      BYTE    StatusBits      상태 비트
        Bit 0: Motor Running
        Bit 1: Alarm Active
        Bit 2: Safety OK
        Bit 3: Auto Mode
19      BYTE    ErrorCode       에러 코드

마커 영역 (M):
M0.0    Motor Start Command
M0.1    Motor Stop Command
M0.2    Alarm Reset
M0.3    Emergency Stop

Note: 실제 S7 서버 구현은 복잡하므로,
      이 시뮬레이터는 TCP 기반 간단한 프로토콜로 구현
      실제 환경에서는 snap7 서버 또는 실제 PLC 사용 권장
"""

import asyncio
import struct
import random
import math
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("S7Simulator")


@dataclass
class PLCMemory:
    """PLC 메모리 시뮬레이션"""
    # Data Blocks
    db: Dict[int, bytearray] = field(default_factory=dict)
    # Markers
    markers: bytearray = field(default_factory=lambda: bytearray(256))
    # Inputs
    inputs: bytearray = field(default_factory=lambda: bytearray(256))
    # Outputs
    outputs: bytearray = field(default_factory=lambda: bytearray(256))

    def __post_init__(self):
        # DB1 초기화 (20 바이트)
        self.db[1] = bytearray(20)


class S7DataSimulator:
    """S7 PLC 데이터 시뮬레이터"""

    def __init__(self, memory: PLCMemory):
        self.memory = memory
        self.start_time = time.time()
        self.motor_running = False
        self.production_count = 0

    def update(self):
        """데이터 업데이트"""
        db1 = self.memory.db[1]

        # 마커 읽기 (명령)
        markers = self.memory.markers
        if markers[0] & 0x01:  # M0.0 - Motor Start
            self.motor_running = True
        if markers[0] & 0x02:  # M0.1 - Motor Stop
            self.motor_running = False
        if markers[0] & 0x08:  # M0.3 - Emergency Stop
            self.motor_running = False

        # 온도 시뮬레이션
        elapsed = time.time() - self.start_time
        temp = 25.0 + 5 * math.sin(elapsed / 3600 * 2 * math.pi)
        temp += random.gauss(0, 0.3)
        struct.pack_into('>f', db1, 0, temp)

        # 습도 시뮬레이션
        humidity = 60.0 + random.gauss(0, 2)
        humidity = max(20, min(90, humidity))
        struct.pack_into('>f', db1, 4, humidity)

        # 압력 시뮬레이션
        pressure = 1.0 + random.gauss(0, 0.02)
        struct.pack_into('>f', db1, 8, pressure)

        # 모터 속도
        if self.motor_running:
            motor_speed = 1500 + int(random.gauss(0, 20))
        else:
            motor_speed = 0
        struct.pack_into('>h', db1, 12, motor_speed)

        # 생산 카운트
        if self.motor_running and random.random() < 0.1:
            self.production_count += 1
        struct.pack_into('>i', db1, 14, self.production_count)

        # 상태 비트
        status = 0
        if self.motor_running:
            status |= 0x01  # Bit 0: Motor Running
        if temp > 35 or humidity > 80:
            status |= 0x02  # Bit 1: Alarm Active
        else:
            status |= 0x04  # Bit 2: Safety OK
        status |= 0x08  # Bit 3: Auto Mode
        db1[18] = status

        # 에러 코드
        error_code = 0
        if temp > 35:
            error_code = 1  # Temperature high
        elif humidity > 80:
            error_code = 2  # Humidity high
        db1[19] = error_code


class S7Protocol:
    """S7 통신 프로토콜 처리"""

    # S7 통신 상수
    COTP_CONNECT = 0xE0
    COTP_DATA = 0xF0
    S7_JOB = 0x01
    S7_ACK_DATA = 0x03

    def __init__(self, memory: PLCMemory):
        self.memory = memory

    def handle_cotp_connect(self, data: bytes) -> bytes:
        """COTP 연결 응답"""
        # COTP Connect Confirm
        response = bytearray([
            0x03, 0x00, 0x00, 0x16,  # TPKT Header
            0x11,                     # COTP Length
            0xD0,                     # COTP Connect Confirm
            0x00, 0x01,              # DST-REF
            0x00, 0x01,              # SRC-REF
            0x00,                     # Class Option
            # Parameters
            0xC0, 0x01, 0x0A,        # TPDU Size
            0xC1, 0x02, 0x01, 0x00,  # SRC-TSAP
            0xC2, 0x02, 0x01, 0x02   # DST-TSAP
        ])
        return bytes(response)

    def handle_s7_setup(self, data: bytes) -> bytes:
        """S7 통신 설정 응답"""
        response = bytearray([
            0x03, 0x00, 0x00, 0x1B,  # TPKT Header
            0x02, 0xF0, 0x80,        # COTP DT Data
            # S7 Header
            0x32,                     # Protocol ID
            0x03,                     # Message Type (Ack_Data)
            0x00, 0x00,              # Reserved
            0x00, 0x01,              # PDU Reference
            0x00, 0x02,              # Parameter Length
            0x00, 0x00,              # Data Length
            0x00,                     # Error Class
            0x00,                     # Error Code
            # Parameters
            0xF0,                     # Function
            0x00                      # Reserved
        ])
        return bytes(response)

    def handle_read_request(self, data: bytes) -> bytes:
        """읽기 요청 처리"""
        # 간단한 응답 생성 (DB1의 모든 데이터)
        db1_data = self.memory.db.get(1, bytearray(20))

        response = bytearray([
            0x03, 0x00, 0x00, 0x00,  # TPKT Header (length will be set)
            0x02, 0xF0, 0x80,        # COTP DT Data
            # S7 Header
            0x32,                     # Protocol ID
            0x03,                     # Message Type (Ack_Data)
            0x00, 0x00,              # Reserved
            0x00, 0x01,              # PDU Reference
            0x00, 0x02,              # Parameter Length
            0x00, len(db1_data) + 4, # Data Length
            0x00,                     # Error Class
            0x00,                     # Error Code
            # Parameters
            0x04,                     # Read Var
            0x01,                     # Item Count
            # Data Item
            0xFF,                     # Return Code (Success)
            0x04,                     # Transport Size (Byte)
            0x00, len(db1_data)      # Length
        ])
        response.extend(db1_data)

        # TPKT 길이 설정
        total_len = len(response)
        response[2] = (total_len >> 8) & 0xFF
        response[3] = total_len & 0xFF

        return bytes(response)

    def handle_write_request(self, data: bytes) -> bytes:
        """쓰기 요청 처리"""
        # 쓰기 성공 응답
        response = bytearray([
            0x03, 0x00, 0x00, 0x16,  # TPKT Header
            0x02, 0xF0, 0x80,        # COTP DT Data
            # S7 Header
            0x32,                     # Protocol ID
            0x03,                     # Message Type (Ack_Data)
            0x00, 0x00,              # Reserved
            0x00, 0x01,              # PDU Reference
            0x00, 0x02,              # Parameter Length
            0x00, 0x01,              # Data Length
            0x00,                     # Error Class
            0x00,                     # Error Code
            # Parameters
            0x05,                     # Write Var
            0x01,                     # Item Count
            # Data Item
            0xFF                      # Return Code (Success)
        ])
        return bytes(response)


class S7Server:
    """S7 TCP 서버"""

    def __init__(self, host: str = '0.0.0.0', port: int = 102):
        self.host = host
        self.port = port
        self.memory = PLCMemory()
        self.simulator = S7DataSimulator(self.memory)
        self.protocol = S7Protocol(self.memory)

    async def handle_client(self, reader: asyncio.StreamReader,
                           writer: asyncio.StreamWriter):
        """클라이언트 연결 처리"""
        addr = writer.get_extra_info('peername')
        logger.info(f"Client connected: {addr}")

        try:
            while True:
                # TPKT Header 읽기 (4 bytes)
                header = await reader.read(4)
                if not header or len(header) < 4:
                    break

                # 패킷 길이 파싱
                length = (header[2] << 8) | header[3]
                if length < 4:
                    continue

                # 나머지 데이터 읽기
                data = await reader.read(length - 4)
                if not data:
                    break

                full_packet = header + data
                response = self.process_packet(full_packet)

                if response:
                    writer.write(response)
                    await writer.drain()

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error handling client {addr}: {e}")
        finally:
            logger.info(f"Client disconnected: {addr}")
            writer.close()
            await writer.wait_closed()

    def process_packet(self, packet: bytes) -> bytes:
        """패킷 처리"""
        if len(packet) < 7:
            return None

        # COTP Type 확인
        cotp_len = packet[4]
        cotp_type = packet[5]

        if cotp_type == 0xE0:  # COTP Connect Request
            logger.debug("COTP Connect Request")
            return self.protocol.handle_cotp_connect(packet)

        elif cotp_type == 0xF0:  # COTP Data
            # S7 메시지 확인
            if len(packet) > 7 + cotp_len:
                s7_start = 4 + cotp_len + 1
                if packet[s7_start] == 0x32:  # S7 Protocol ID
                    msg_type = packet[s7_start + 1]
                    if msg_type == 0x01:  # Job
                        func = packet[s7_start + 17] if len(packet) > s7_start + 17 else 0

                        if func == 0xF0:  # Setup Communication
                            logger.debug("S7 Setup Communication")
                            return self.protocol.handle_s7_setup(packet)
                        elif func == 0x04:  # Read Var
                            logger.debug("S7 Read Request")
                            return self.protocol.handle_read_request(packet)
                        elif func == 0x05:  # Write Var
                            logger.debug("S7 Write Request")
                            return self.protocol.handle_write_request(packet)

        return None

    async def update_loop(self):
        """데이터 업데이트 루프"""
        while True:
            self.simulator.update()
            await asyncio.sleep(1)

    async def start(self):
        """서버 시작"""
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )

        logger.info("=" * 50)
        logger.info("MING Stack - S7 PLC Simulator")
        logger.info("=" * 50)
        logger.info(f"Listening on {self.host}:{self.port}")
        logger.info("")
        logger.info("DB1 Structure:")
        logger.info("  Offset 0:  Temperature (REAL)")
        logger.info("  Offset 4:  Humidity (REAL)")
        logger.info("  Offset 8:  Pressure (REAL)")
        logger.info("  Offset 12: MotorSpeed (INT)")
        logger.info("  Offset 14: ProductCount (DINT)")
        logger.info("  Offset 18: StatusBits (BYTE)")
        logger.info("  Offset 19: ErrorCode (BYTE)")
        logger.info("=" * 50)

        # 업데이트 루프 시작
        asyncio.create_task(self.update_loop())

        async with server:
            await server.serve_forever()


async def main():
    server = S7Server()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
