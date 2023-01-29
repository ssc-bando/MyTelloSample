import socket
import threading
import cv2
import time

# Tello機体状態の保存先パス
status_file_path = "/tmp/tello_status.csv"
# ドローンTelloカメラ動画の保存先パス
file_path = "/tmp/tello.avi"


# Tello自動操縦用の関数
def tello_ctrl():
    global end_flag

    # ここに操作したいコードを記載
    sock_cm.sendto("takeoff".encode('utf-8'), TELLO_ADDRESS)
    time.sleep(10)
    sock_cm.sendto("land".encode('utf-8'), TELLO_ADDRESS)
    time.sleep(5)

    # 操作完了したのでプログラム終了を伝える
    end_flag = True


# Tello機体ステータス 受け取り用の関数
def udp_receiver_status(sock):
    global end_flag
    global tello_status

    while end_flag is False:
        try:
            response, _ = sock.recvfrom(1024)
            # 機体ステータスをグローバル変数に格納
            tello_status = response.decode('utf-8')
        except Exception as e:
            print(e)
            break


# Telloコマンド結果 受け取り用の関数
def udp_receiver_command(sock):
    global end_flag
    global tello_response

    while end_flag is False:
        try:
            response, _ = sock.recvfrom(1024)
            # コマンドの応答結果をグローバル変数に格納
            tello_response = response.decode('utf-8')
        except Exception as e:
            print(e)
            break


# 出力動画フォーマット
fmt = cv2.VideoWriter_fourcc('h', '2', '6', '4')
fps = 30
size = (960, 720)
writer = cv2.VideoWriter(file_path, fmt, fps, size)

# 変数
end_flag         = False
tello_response   = ''
tello_status     = ''
tello_all_status = ''
frame_skip       = 60

# TelloのIPアドレス、ポート(コマンド用)、ポート(機体ステータス用)
TELLO_IP      = '192.168.10.1'
TELLO_CM_PORT = 8889
TELLO_ST_PORT = 8890
TELLO_ADDRESS = (TELLO_IP, TELLO_CM_PORT)

# Telloからの映像受信用のローカルIPアドレス、宛先ポート番号
TELLO_CAM_ADDRESS = 'udp://@0.0.0.0:11111?overrun_nonfatal=1&fifo_size=50000000'

# UDP通信用ソケットを作成してBIND
sock_cm = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_cm.bind(('', TELLO_CM_PORT))
sock_st.bind(('', TELLO_ST_PORT))

# コマンド送信結果　受信用スレッドの作成
thread_cm = threading.Thread(target=udp_receiver_command, args=(sock_cm,))
thread_cm.daemon = True
thread_cm.start()

# 機体ステータス　　受信用スレッドの作成
thread_st = threading.Thread(target=udp_receiver_status, args=(sock_st,))
thread_st.daemon = True
thread_st.start()

# Tello側がコマンド受付の準備が間に合っていない場合がある
# ここだけはしっかりとループでcommand応答が返るまで待つ
tello_response = ''
while True:
    # コマンドモード
    sock_cm.sendto('command'.encode('utf-8'), TELLO_ADDRESS)
    time.sleep(1)
    if tello_response == 'ok':
        print("command response OK")
        break
    print("wait for command response...")

# Telloのバッテリ取得
sock_cm.sendto('battery?'.encode('utf-8'), TELLO_ADDRESS)
time.sleep(1)
print('Tello Battery: ' + tello_response.strip() + '%')

# 飛行できる分のバッテリ残量が無い場合はプログラムを終了
if int(tello_response) < 20:
    print("Error: Low Battery")
    exit()

# カメラ映像のストリーミング開始)
sock_cm.sendto('streamon'.encode('utf-8'), TELLO_ADDRESS)

# Telloカメラ映像のキャプチャ(５～６秒時間がかかる)
cap = cv2.VideoCapture(TELLO_CAM_ADDRESS)
cap.open(TELLO_CAM_ADDRESS)

# Tello自動操縦スレッドの作成
thread_tello = threading.Thread(target=tello_ctrl)
thread_tello.daemon = True
thread_tello.start()

print("Drone Control Program : Start")

# メインループ処理
try:
    while end_flag is False:
        ret, frame = cap.read()

        # 最初のフレームをある程度捨ててから録画開始
        if 0 < frame_skip:
            frame_skip = frame_skip - 1
            continue

        # 動画フレームが空の時の処理　現状不要？
        if frame is None or frame.size == 0:
            print("frame.size 0")
            continue

        # 動画ファイルとして書き込み
        writer.write(frame)
        # Tello機体情報を記録(動画フレーム数に同期させて記録)
        tello_all_status = tello_all_status + tello_status

except Exception as ex:
    print(ex)
    # 異常時は念のため着陸コマンド送ってから終わらせる
    sock_cm.sendto("land".encode('utf-8'), TELLO_ADDRESS)
    time.sleep(5)
    end_flag = True
finally:
    print("Drone Control Program : END")

    # Tello機体情報をファイルに出力する
    f = open(status_file_path, 'w')
    f.write(tello_all_status)
    f.close()

    # ビデオストリーミング停止
    sock_cm.sendto('streamoff'.encode('utf-8'), TELLO_ADDRESS)
    writer.release()
    cap.release()
