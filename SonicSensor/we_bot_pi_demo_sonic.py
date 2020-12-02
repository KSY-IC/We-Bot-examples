#-------------------------------------------------------------------------------------#
# We-Bot Pi デモ走行用プログラム(Ver.2 2020/11/11)
#-------------------------------------------------------------------------------------#
# ソフトウェアを利用するにあたっての注意点（必ず確認して下さい）
# ・本ソフトウェアは(株)ケイエスワイがデモ用に作成したソフトです。
# ・本ソフトウェアの利用にあたっては、全て利用者の自己責任で行って下さい。
# ・本ソフトウェアの改変、流用は全て利用者の責任において、自由に行って構いません。
# ・本ソフトウェアを使用して発生したあらゆる損害（金銭的損害、物理的損害等）は
#   全て利用者の責任において負担し、作者はいかなる損害も補償しません。
# ・本ソフトウェアの配布等に関しては、全て配布者の責任において行い、
#   作者は一切の責任を負わないものとします。
# ・作者は本ソフトウェアに関しての問い合わせ等には一切ご対応致しません。

#-------------------------------------------------------------------------------------#
# ライブラリ
#-------------------------------------------------------------------------------------#
import time
import random
import pigpio
from webot import WeBot


#-------------------------------------------------------------------------------------#
# 定数定義
#-------------------------------------------------------------------------------------#
RETURN_VALUE_SUCCESS = 0        # 戻り値 正常時
RETURN_VALUE_ERROR = -1         # 戻り値 エラー時

GPIO_SONIC_TRIG = 26            # 超音波センサTRIGピン GPIO番号(BCM)
GPIO_SONIC_ECHO = 19            # 超音波センサECHOピン GPIO番号(BCM)

CYCLE_TIME_SEC = 5              # 旋回周期
BACK_TIME_SEC = 0.5             # バック時間
TURN_TIME_SEC_MIN = 2.0         # 最小旋回時間
TURN_TIME_SEC_MAX = 5.0         # 最大旋回時間

DISTANCE_THRESHOLD = 0.1        # 距離センサしきい値
BATTERY_LOW_VOLTAGE = 5.8       # バッテリー低下しきい値

MOTOR_SPEED = 400
MOTOR_LEFT_OFFSET = 1.0
MOTOR_RIGHT_OFFSET = 1.0

#-------------------------------------------------------------------------------------#
# 関数
#-------------------------------------------------------------------------------------#

#--------------------------
# Sonic distance sensor
#--------------------------
#-------------------------------------------------------------------------------------#
# 関数
#-------------------------------------------------------------------------------------#
gpio = pigpio.pi()
webot_pi = WeBot()


def init_hcsr04(trig_pin=26, echo_pin=19 ):
    """
    超音波センサ関連のGPIOを初期化する
    :param trig_pin: トリガピン番号(default: 26)
    :param echo_pin: エコーピン番号(default: 19)
    :return: なし
    """
    # GPIOの初期化
    gpio.set_mode(trig_pin, pigpio.OUTPUT)
    gpio.set_mode(echo_pin, pigpio.INPUT)
    gpio.write(trig_pin, 0)
    

def measure_pulse_time(echo_pin=19, pin_value=1, timeout=0.25):
    """
    ECHOピンに入力されるパルスの幅を測定する
    :param echo_pin: ECHOのGPIO 番号(default:GPIO19)
    :param pin_value: ECHOピンのレベル指定(GPIO.HIGH or GPIO.LOW default:GPIO.HIGH)
    :param timeout: タイムアウト(default:0.25sec)
    :return: パルスの長さ(sec) タイムアウト時は0
    """

    start_time = time.time()
    pin_inv_value = not pin_value

    # 前のパルスが終了するのを待つ
    while gpio.read(echo_pin) == pin_value:
        if time.time() - start_time > timeout:
            return RETURN_VALUE_ERROR

    # パルスの開始を待ち、時刻を記録する
    while gpio.read(echo_pin) == pin_inv_value:
        if time.time() - start_time > timeout:
            return RETURN_VALUE_ERROR
    
    pulse_start_time = time.time()

    # パルスが終了するのを待ち、時刻を記録する
    while gpio.read(echo_pin) == pin_value:
        if time.time() - start_time > timeout:
            return RETURN_VALUE_ERROR

    pulse_end_time = time.time()

    return pulse_end_time - pulse_start_time


def get_distance_hcsr04(trig_pin=26, echo_pin=19, temp=25):
    """
    超音波センサHC-SR04から距離を取得する
    :param trig_pin: TRIGのGPIO 番号(default:GPIO26)
    :param echo_pin: ECHOのGPIO 番号(default:GPIO19)
    :param temp: 音波速度補正用の温度(default:25)
    :return: 距離(m) タイムアウト時は0
    """

    # 出力を初期化
    gpio.write(trig_pin, 0)
    time.sleep(0.3)

    # 出力(10us以上待つ)
    gpio.write(trig_pin, 1)
    time.sleep(0.00001)

    # 出力停止
    gpio.write(trig_pin, 0)

    # echoから
    echo_time = measure_pulse_time(echo_pin, 1)
    echo_dinstance = (331.5 + 0.61 * temp) * echo_time / 2

    return echo_dinstance




def go_backword(time_sec=BACK_TIME_SEC):
    """
    指定時間バックする
    :param time_sec: バックする時間(sec)
    :return: なし
    """

    webot_pi.back(MOTOR_SPEED)
    time.sleep(time_sec)


def random_spin_turn(time_sec_min=TURN_TIME_SEC_MIN, time_sec_max=TURN_TIME_SEC_MAX, direction=0):
    """
    ランダム時間スピンターンする
    :param time_sec_min: 最小旋回時間(sec)
    :param time_sec_max: 最大旋回時間(sec)
    :direction: 最大旋回時間(sec)
    :return: なし
    """

    # スピンターン
    random_sec = random.uniform(time_sec_min, time_sec_max)
    if direction == 0:
        webot_pi.left(MOTOR_SPEED) 
    elif direction == 1:
        print('motor_spin_turn_right')
        webot_pi.right(MOTOR_SPEED) 

    time.sleep(random_sec)
    print('motor_stop')
    webot_pi.stop()


def check_battery_voltage(min_voltage=BATTERY_LOW_VOLTAGE):
    """
    バッテリー電圧がしきい値を下回っていないか確認する
    :param portname: UARTポート
    :param min_voltage: バッテリー低下しきい値(mv)
    :return: 正常:0、低下:-1
    """

    # バッテリー電圧のチェック
    volgate = webot_pi.readVoltage(2)
    print('Battery Volgage= %d V' % volgate)
    if volgate < BATTERY_LOW_VOLTAGE:
        print('Error: Low Battery!')
        return RETURN_VALUE_ERROR
    else:
        return RETURN_VALUE_SUCCESS


def main():
    """
    デモ走行用メインプログラム（超音波センサあり）
    走行中に超音波センサが一定距離を下回るとランダムに旋回する
    定期的にランダムに旋回する
    :param: なし
    :return: なし
    """

    # Initialize Motor Driver
    webot_pi.enableMotor()
    webot_pi.setSpeedOffset(MOTOR_LEFT_OFFSET, MOTOR_RIGHT_OFFSET)

    try:
        # 超音波センサのGPIO初期化
        init_hcsr04(GPIO_SONIC_TRIG, GPIO_SONIC_ECHO)

        # 停止
        print('motor_stop')
        webot_pi.stop()
        time.sleep(0.5)

        start_time = time.time()        # 直進開始時間を取得

        while True:
            # バッテリー電圧のチェック
            battery_status = check_battery_voltage( BATTERY_LOW_VOLTAGE)

            if battery_status == RETURN_VALUE_ERROR:    # 低下時
                battery_status = check_battery_voltage( BATTERY_LOW_VOLTAGE)  # 再度電圧チェック

                if battery_status == RETURN_VALUE_ERROR:    # 2回連続で低下していたらエラー終了
                    webot_pi.stop()         # モーター停止
                    webot_pi.disableMotor()
                    exit(1)     # プログラム終了

            pass_time = time.time() - start_time    # 直進経過時間を確認

            if pass_time > CYCLE_TIME_SEC:      # 直進で一定時間経過したら向きを変える
                # 停止
                print('motor_stop')
                webot_pi.stop()
                time.sleep(0.5)

                # バック
                print('motor_reverse')
                go_backword(BACK_TIME_SEC)
                time.sleep(0.5)

                # スピンターン
                turn_direction = random.randint(0, 1)   # 旋回方向はランダム
                print('motor_spin_turn')
                random_spin_turn(direction=turn_direction)
                time.sleep(0.5)

                start_time = time.time()        # 直進開始時間を新規取得

            # 超音波センサの距離取得
            distance = get_distance_hcsr04(GPIO_SONIC_TRIG, GPIO_SONIC_ECHO)
            print('distance= %1.3f m' % distance)

            if distance > DISTANCE_THRESHOLD:       # しきい値よりも前方の距離が大きい場合
                print('motor_forward')
                webot_pi.forward(MOTOR_SPEED)
            elif distance < 0:                      # 測距エラーの場合
                webot_pi.stop()
                time.sleep(0.5)
                print('Error: Sonic Sensor')

                distance = get_distance_hcsr04(GPIO_SONIC_TRIG, GPIO_SONIC_ECHO)
                if distance < 0:        # 2回連続で測距エラーの場合
                    exit(1)     # プログラム終了
            else:               # 前方の距離がしきい値よりも小さい場合
                # 停止
                print('motor_stop')
                webot_pi.stop()
                time.sleep(0.5)

                # バック
                print('motor_reverse')
                go_backword(BACK_TIME_SEC)
                time.sleep(0.5)

                # 停止
                print('motor_stop')
                webot_pi.stop()
                time.sleep(0.5)

                # スピンターン
                turn_direction = random.randint(0, 1)   # 旋回方向はランダム
                print('motor_spin_turn')
                random_spin_turn(direction=turn_direction)
                time.sleep(0.5)
                start_time = time.time()
                
    # 例外処理
    except KeyboardInterrupt:       # Ctrl+Cで停止させた場合
        print('Keyboard Interruption')
        print('motor_stop')
        webot_pi.stop()
        webot_pi.disableMotor()

    except Exception as e:
        print('Error: Exception in main')
        print('motor_stop')
        webot_pi.stop()
        webot_pi.disableMotor()
        print(type(e))
        print(e.args)
        print(e)


if __name__ == '__main__':
    main()