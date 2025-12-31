#!/usr/bin/env python3
"""
OPC-UA Server Simulator for MING Stack
산업용 표준 OPC-UA 서버 시뮬레이션

노드 구조:
├── Objects
│   └── Factory
│       ├── Line1
│       │   ├── Temperature (Float)
│       │   ├── Humidity (Float)
│       │   ├── Pressure (Float)
│       │   └── Sensors
│       │       ├── Sensor001
│       │       └── Sensor002
│       ├── Line2
│       │   └── ...
│       └── ProductionData
│           ├── TotalCount (Int)
│           ├── GoodCount (Int)
│           ├── DefectCount (Int)
│           └── OEE (Float)
"""

import asyncio
import random
import math
import time
import logging
from datetime import datetime
from asyncua import Server, ua
from asyncua.common.methods import uamethod

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OpcUaSimulator")


class ProductionSimulator:
    """생산 데이터 시뮬레이터"""

    def __init__(self):
        self.start_time = time.time()
        self.total_count = 0
        self.good_count = 0
        self.defect_count = 0

    def simulate_production(self):
        """생산 시뮬레이션"""
        # 10% 확률로 생산
        if random.random() < 0.1:
            self.total_count += 1
            # 95% 양품률
            if random.random() < 0.95:
                self.good_count += 1
            else:
                self.defect_count += 1

    def get_oee(self):
        """OEE (Overall Equipment Effectiveness) 계산"""
        if self.total_count == 0:
            return 0.0
        availability = 0.95  # 95% 가동률 가정
        performance = min(1.0, self.total_count / 100)  # 목표 대비 성과
        quality = self.good_count / self.total_count if self.total_count > 0 else 0
        return availability * performance * quality * 100


class SensorSimulator:
    """센서 데이터 시뮬레이터"""

    def __init__(self, base_temp=25, base_humidity=60, base_pressure=1.0):
        self.start_time = time.time()
        self.base_temp = base_temp
        self.base_humidity = base_humidity
        self.base_pressure = base_pressure

    def get_temperature(self):
        """온도 시뮬레이션"""
        elapsed = time.time() - self.start_time
        variation = 5 * math.sin(elapsed / 3600 * 2 * math.pi)
        noise = random.gauss(0, 0.3)
        return round(self.base_temp + variation + noise, 2)

    def get_humidity(self):
        """습도 시뮬레이션"""
        elapsed = time.time() - self.start_time
        variation = -10 * math.sin(elapsed / 3600 * 2 * math.pi)
        noise = random.gauss(0, 1)
        humidity = self.base_humidity + variation + noise
        return round(max(20, min(90, humidity)), 2)

    def get_pressure(self):
        """압력 시뮬레이션"""
        noise = random.gauss(0, 0.01)
        return round(self.base_pressure + noise, 3)

    def get_motor_speed(self):
        """모터 속도 시뮬레이션"""
        base_speed = 1500
        variation = random.gauss(0, 20)
        return round(base_speed + variation, 1)

    def get_vibration(self):
        """진동 시뮬레이션"""
        return round(random.uniform(0.1, 2.0), 3)

    def get_power(self):
        """전력 소비 시뮬레이션"""
        base_power = 45
        variation = random.gauss(0, 3)
        return round(base_power + variation, 2)


# OPC-UA 메서드 정의
@uamethod
def start_motor(parent):
    """모터 시작 메서드"""
    logger.info("Motor START command received")
    return ua.StatusCode(ua.StatusCodes.Good)


@uamethod
def stop_motor(parent):
    """모터 정지 메서드"""
    logger.info("Motor STOP command received")
    return ua.StatusCode(ua.StatusCodes.Good)


@uamethod
def reset_counter(parent):
    """카운터 리셋 메서드"""
    logger.info("Counter RESET command received")
    return ua.StatusCode(ua.StatusCodes.Good)


async def main():
    """OPC-UA 서버 메인 함수"""

    logger.info("=" * 50)
    logger.info("MING Stack - OPC-UA Server Simulator")
    logger.info("=" * 50)

    # 서버 생성
    server = Server()
    await server.init()

    server.set_endpoint("opc.tcp://0.0.0.0:4840")
    server.set_server_name("MING Stack OPC-UA Simulator")

    # 네임스페이스 등록
    uri = "http://ming-stack.local/opcua"
    idx = await server.register_namespace(uri)

    # 객체 폴더 가져오기
    objects = server.nodes.objects

    # Factory 객체 생성
    factory = await objects.add_object(idx, "Factory")

    # Line1 생성
    line1 = await factory.add_object(idx, "Line1")

    # Line1 센서 변수
    line1_temp = await line1.add_variable(idx, "Temperature", 25.0)
    line1_humidity = await line1.add_variable(idx, "Humidity", 60.0)
    line1_pressure = await line1.add_variable(idx, "Pressure", 1.0)
    line1_motor_speed = await line1.add_variable(idx, "MotorSpeed", 0.0)
    line1_vibration = await line1.add_variable(idx, "Vibration", 0.0)
    line1_power = await line1.add_variable(idx, "PowerConsumption", 0.0)

    # 쓰기 가능 설정
    await line1_motor_speed.set_writable()

    # Line2 생성
    line2 = await factory.add_object(idx, "Line2")
    line2_temp = await line2.add_variable(idx, "Temperature", 26.0)
    line2_humidity = await line2.add_variable(idx, "Humidity", 58.0)
    line2_pressure = await line2.add_variable(idx, "Pressure", 1.02)
    line2_motor_speed = await line2.add_variable(idx, "MotorSpeed", 0.0)

    # 생산 데이터 객체
    production = await factory.add_object(idx, "ProductionData")
    prod_total = await production.add_variable(idx, "TotalCount", 0)
    prod_good = await production.add_variable(idx, "GoodCount", 0)
    prod_defect = await production.add_variable(idx, "DefectCount", 0)
    prod_oee = await production.add_variable(idx, "OEE", 0.0)

    # 메서드 추가
    await line1.add_method(idx, "StartMotor", start_motor, [], [])
    await line1.add_method(idx, "StopMotor", stop_motor, [], [])
    await production.add_method(idx, "ResetCounter", reset_counter, [], [])

    # 알람 및 이벤트 객체
    alarms = await factory.add_object(idx, "Alarms")
    alarm_temp_high = await alarms.add_variable(idx, "TemperatureHigh", False)
    alarm_humidity_high = await alarms.add_variable(idx, "HumidityHigh", False)
    alarm_motor_fault = await alarms.add_variable(idx, "MotorFault", False)

    # 시스템 상태
    system = await factory.add_object(idx, "System")
    sys_uptime = await system.add_variable(idx, "Uptime", 0)
    sys_timestamp = await system.add_variable(idx, "LastUpdate", datetime.now())

    logger.info(f"Endpoint: opc.tcp://0.0.0.0:4840")
    logger.info(f"Namespace: {uri} (idx={idx})")
    logger.info("")
    logger.info("Node Structure:")
    logger.info("├── Factory")
    logger.info("│   ├── Line1")
    logger.info("│   │   ├── Temperature, Humidity, Pressure")
    logger.info("│   │   ├── MotorSpeed, Vibration, PowerConsumption")
    logger.info("│   │   └── Methods: StartMotor, StopMotor")
    logger.info("│   ├── Line2")
    logger.info("│   │   └── Temperature, Humidity, Pressure, MotorSpeed")
    logger.info("│   ├── ProductionData")
    logger.info("│   │   ├── TotalCount, GoodCount, DefectCount, OEE")
    logger.info("│   │   └── Methods: ResetCounter")
    logger.info("│   ├── Alarms")
    logger.info("│   │   └── TemperatureHigh, HumidityHigh, MotorFault")
    logger.info("│   └── System")
    logger.info("│       └── Uptime, LastUpdate")
    logger.info("=" * 50)

    # 시뮬레이터 인스턴스
    sensor1 = SensorSimulator(25, 60, 1.0)
    sensor2 = SensorSimulator(26, 58, 1.02)
    prod_sim = ProductionSimulator()

    async with server:
        while True:
            try:
                # Line1 데이터 업데이트
                await line1_temp.write_value(sensor1.get_temperature())
                await line1_humidity.write_value(sensor1.get_humidity())
                await line1_pressure.write_value(sensor1.get_pressure())
                await line1_motor_speed.write_value(sensor1.get_motor_speed())
                await line1_vibration.write_value(sensor1.get_vibration())
                await line1_power.write_value(sensor1.get_power())

                # Line2 데이터 업데이트
                await line2_temp.write_value(sensor2.get_temperature())
                await line2_humidity.write_value(sensor2.get_humidity())
                await line2_pressure.write_value(sensor2.get_pressure())
                await line2_motor_speed.write_value(sensor2.get_motor_speed())

                # 생산 데이터 업데이트
                prod_sim.simulate_production()
                await prod_total.write_value(prod_sim.total_count)
                await prod_good.write_value(prod_sim.good_count)
                await prod_defect.write_value(prod_sim.defect_count)
                await prod_oee.write_value(prod_sim.get_oee())

                # 알람 체크
                temp1 = await line1_temp.read_value()
                humidity1 = await line1_humidity.read_value()
                await alarm_temp_high.write_value(temp1 > 35)
                await alarm_humidity_high.write_value(humidity1 > 80)

                # 시스템 상태 업데이트
                uptime = int(time.time() - sensor1.start_time)
                await sys_uptime.write_value(uptime)
                await sys_timestamp.write_value(datetime.now())

            except Exception as e:
                logger.error(f"Error updating values: {e}")

            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
