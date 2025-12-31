#!/usr/bin/env python3
"""
Modbus TCP Simulator for MING Stack
산업용 센서/PLC 데이터 시뮬레이션

레지스터 맵:
- Holding Registers (FC 03/06/16):
  - 0: 온도 (x0.1 °C) - 예: 255 = 25.5°C
  - 1: 습도 (x0.1 %) - 예: 602 = 60.2%
  - 2: 압력 (x0.01 bar) - 예: 120 = 1.20 bar
  - 3: 모터 속도 (RPM)
  - 4: 전류 (x0.01 A)
  - 5: 전압 (x0.1 V)
  - 6: 전력 (W)
  - 7: 생산 카운트
  - 8: 에러 코드
  - 9: 상태 비트

- Input Registers (FC 04):
  - 0-9: 읽기 전용 센서 값

- Coils (FC 01/05/15):
  - 0: 모터 시작/정지
  - 1: 알람 리셋
  - 2: 비상 정지
  - 3-9: 예비

- Discrete Inputs (FC 02):
  - 0: 모터 운전 중
  - 1: 알람 활성
  - 2: 안전 상태
  - 3-9: 예비
"""

import asyncio
import random
import math
import time
import logging
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
    ModbusServerContext
)
from pymodbus.device import ModbusDeviceIdentification

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ModbusSimulator")


class IndustrialDataSimulator:
    """산업용 센서 데이터 시뮬레이터"""

    def __init__(self):
        self.start_time = time.time()
        self.base_temp = 25.0
        self.base_humidity = 60.0
        self.base_pressure = 1.0
        self.motor_running = False
        self.motor_speed = 0
        self.production_count = 0
        self.alarm_active = False

    def get_temperature(self):
        """온도 시뮬레이션 (일교차 패턴)"""
        elapsed = time.time() - self.start_time
        # 사인파 기반 온도 변화 (주기: 1시간)
        variation = 5 * math.sin(elapsed / 3600 * 2 * math.pi)
        noise = random.gauss(0, 0.5)
        temp = self.base_temp + variation + noise
        return int(temp * 10)  # x0.1 스케일

    def get_humidity(self):
        """습도 시뮬레이션"""
        elapsed = time.time() - self.start_time
        # 온도와 반대 패턴
        variation = -10 * math.sin(elapsed / 3600 * 2 * math.pi)
        noise = random.gauss(0, 2)
        humidity = self.base_humidity + variation + noise
        humidity = max(20, min(90, humidity))  # 20-90% 범위 제한
        return int(humidity * 10)

    def get_pressure(self):
        """압력 시뮬레이션"""
        noise = random.gauss(0, 0.02)
        pressure = self.base_pressure + noise
        return int(pressure * 100)

    def get_motor_data(self):
        """모터 데이터 시뮬레이션"""
        if self.motor_running:
            # 모터 속도 (목표: 1500 RPM)
            target_speed = 1500
            if self.motor_speed < target_speed:
                self.motor_speed = min(target_speed, self.motor_speed + 50)
            noise = random.gauss(0, 10)
            speed = self.motor_speed + noise

            # 전류 (속도에 비례)
            current = (speed / 1500) * 5 + random.gauss(0, 0.1)

            # 전력
            power = speed * current * 0.8 / 100
        else:
            if self.motor_speed > 0:
                self.motor_speed = max(0, self.motor_speed - 100)
            speed = self.motor_speed
            current = 0.1  # 대기 전류
            power = 5  # 대기 전력

        return {
            'speed': int(speed),
            'current': int(current * 100),
            'voltage': int(380 * 10),  # 380V
            'power': int(power)
        }

    def update_production(self):
        """생산량 업데이트"""
        if self.motor_running and random.random() < 0.1:  # 10% 확률로 생산
            self.production_count += 1
        return self.production_count

    def check_alarm(self, temp, humidity, pressure):
        """알람 조건 체크"""
        temp_celsius = temp / 10
        humidity_pct = humidity / 10
        pressure_bar = pressure / 100

        # 알람 조건
        if temp_celsius > 35 or temp_celsius < 15:
            self.alarm_active = True
            return 1  # 온도 알람
        elif humidity_pct > 80 or humidity_pct < 30:
            self.alarm_active = True
            return 2  # 습도 알람
        elif pressure_bar > 1.3 or pressure_bar < 0.7:
            self.alarm_active = True
            return 3  # 압력 알람
        else:
            self.alarm_active = False
            return 0


async def update_registers(context):
    """레지스터 값 주기적 업데이트"""
    simulator = IndustrialDataSimulator()
    slave_id = 0x01

    logger.info("Starting register update loop...")

    while True:
        try:
            # 센서 데이터 생성
            temp = simulator.get_temperature()
            humidity = simulator.get_humidity()
            pressure = simulator.get_pressure()
            motor = simulator.get_motor_data()
            production = simulator.update_production()
            error_code = simulator.check_alarm(temp, humidity, pressure)

            # Coils 읽기 (모터 제어 명령)
            coils = context[slave_id].getValues(1, 0, 3)
            if coils[0]:  # 모터 시작 명령
                simulator.motor_running = True
            if coils[2]:  # 비상 정지
                simulator.motor_running = False
                simulator.motor_speed = 0
            if coils[1]:  # 알람 리셋
                simulator.alarm_active = False
                # 리셋 후 코일 해제
                context[slave_id].setValues(1, 1, [False])

            # 상태 비트
            status = 0
            status |= (1 if simulator.motor_running else 0)
            status |= (2 if simulator.alarm_active else 0)
            status |= (4 if not simulator.alarm_active else 0)  # 안전 상태

            # Holding Registers 업데이트
            holding_values = [
                temp,           # 0: 온도
                humidity,       # 1: 습도
                pressure,       # 2: 압력
                motor['speed'], # 3: 모터 속도
                motor['current'],  # 4: 전류
                motor['voltage'],  # 5: 전압
                motor['power'],    # 6: 전력
                production,     # 7: 생산 카운트
                error_code,     # 8: 에러 코드
                status          # 9: 상태 비트
            ]
            context[slave_id].setValues(3, 0, holding_values)

            # Input Registers 업데이트 (읽기 전용 미러)
            context[slave_id].setValues(4, 0, holding_values)

            # Discrete Inputs 업데이트
            discrete_inputs = [
                simulator.motor_running,
                simulator.alarm_active,
                not simulator.alarm_active  # 안전 상태
            ]
            context[slave_id].setValues(2, 0, discrete_inputs)

            logger.debug(
                f"Updated: Temp={temp/10}°C, Humidity={humidity/10}%, "
                f"Pressure={pressure/100}bar, Motor={motor['speed']}RPM"
            )

        except Exception as e:
            logger.error(f"Error updating registers: {e}")

        await asyncio.sleep(1)  # 1초마다 업데이트


async def run_server():
    """Modbus TCP 서버 실행"""

    # 데이터 블록 초기화
    # Coils, Discrete Inputs, Input Registers, Holding Registers
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [False] * 100),  # Discrete Inputs
        co=ModbusSequentialDataBlock(0, [False] * 100),  # Coils
        hr=ModbusSequentialDataBlock(0, [0] * 100),      # Holding Registers
        ir=ModbusSequentialDataBlock(0, [0] * 100)       # Input Registers
    )

    context = ModbusServerContext(slaves={0x01: store}, single=False)

    # 디바이스 식별 정보
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'MING Stack'
    identity.ProductCode = 'MODBUS-SIM'
    identity.VendorUrl = 'https://github.com/ming-stack'
    identity.ProductName = 'Industrial Modbus Simulator'
    identity.ModelName = 'MING-MODBUS-001'
    identity.MajorMinorRevision = '1.0.0'

    logger.info("=" * 50)
    logger.info("MING Stack - Modbus TCP Simulator")
    logger.info("=" * 50)
    logger.info(f"Listening on port 5020")
    logger.info("Register Map:")
    logger.info("  HR 0: Temperature (x0.1 °C)")
    logger.info("  HR 1: Humidity (x0.1 %)")
    logger.info("  HR 2: Pressure (x0.01 bar)")
    logger.info("  HR 3: Motor Speed (RPM)")
    logger.info("  HR 4: Current (x0.01 A)")
    logger.info("  HR 5: Voltage (x0.1 V)")
    logger.info("  HR 6: Power (W)")
    logger.info("  HR 7: Production Count")
    logger.info("  HR 8: Error Code")
    logger.info("  HR 9: Status Bits")
    logger.info("=" * 50)

    # 레지스터 업데이트 태스크 시작
    asyncio.create_task(update_registers(context))

    # 서버 시작
    await StartAsyncTcpServer(
        context=context,
        identity=identity,
        address=("0.0.0.0", 5020)
    )


if __name__ == "__main__":
    asyncio.run(run_server())
