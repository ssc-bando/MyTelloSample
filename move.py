import socket

TELLO_IP      = '192.168.10.1'
TELLO_CM_PORT = 8889
TELLO_ST_PORT = 8890
TELLO_ADDRESS = (TELLO_IP, TELLO_CM_PORT)


class TelloSock:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = self.sock_initialize()

    def sock_initialize(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', self._port))
        return s

    def send(self, cmd):
        addr = (self._host, self._port)
        self._sock.sendto(cmd.encode('utf-8'), addr)

    def recv(self):
        try:
            r, _ = self._sock.recvfrom(1024)
            r_text = r.decode('utf-8')
        except Exception as e:
            print(e)
            return ""
        return r_text


class TelloCommand:
    def __init__(self):
        self._cmd    = TelloSock(TELLO_IP, TELLO_CM_PORT)
        self._status = TelloSock(TELLO_IP, TELLO_ST_PORT)

    def command(self, cmd):
        print(">> [%s]" % cmd)
        self._cmd.send(cmd)
        ret = self._cmd.recv()
        print("<< [%s]" % ret)
        return ret

    def status(self):
        r = self._status.recv()
        print("status [%s]" % r)
        return r


class TelloControl:
    def __init__(self):
        self._cmd = TelloCommand()

    def enter_command_mode(self):
        while True:
            # コマンドモード
            r = self._cmd.command('command')
            if r == 'ok':
                print("command response OK")
                break
            print("wait for command response...")

    def has_enough_battery(self):
        r = self._cmd.command('battery?')
        print('Tello Battery: ' + r.strip() + '%')
        # 飛行できる分のバッテリ残量が無い場合はプログラムを終了
        if int(r) < 20:
            print("Error: Low Battery")
            return False
        return True

    def initialize(self):
        self.enter_command_mode()
        if self.has_enough_battery() is False:
            return False
        return True

    def command(self, cmd):
        self._cmd.command(cmd)


def main():
    ctrl = TelloControl()
    if ctrl.initialize() is False:
        exit()
    ctrl.command("takeoff")
    ctrl.command("land")
    print("Drone Control Program : Start")


if __name__ == "__main__":
    main()
