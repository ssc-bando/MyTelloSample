import socket

TELLO_IP          = '192.168.10.1'
TELLO_CM_PORT     = 8889
TELLO_ST_PORT     = 8890
TELLO_ADDRESS     = (TELLO_IP, TELLO_CM_PORT)
TELLO_CAM_ADDRESS = 'udp://@0.0.0.0:11111?overrun_nonfatal=1&fifo_size=50000000'


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

    def send(self, cmd):
        print(">> [%s]" % cmd)
        self._cmd.send(cmd)
        ret = self._cmd.recv()
        print("<< [%s]" % ret.strip())
        return ret

    def status(self):
        r = self._status.recv()
        print("status [%s]" % r)
        return r

    def command(self):
        return self.send('command')

    def takeoff(self):
        return self.send('takeoff')

    def land(self):
        return self.send('land')

    def streamon(self):
        return self.send('streamon')

    def streamoff(self):
        return self.send('streamoff')

    def emergency(self):
        return self.send('emergency')

    def up(self, cm):
        return self.send('up %d' % cm)

    def down(self, cm):
        return self.send('down %d' % cm)

    def left(self, cm):
        return self.send('left %d' % cm)

    def right(self, cm):
        return self.send('right %d' % cm)

    def forward(self, cm):
        return self.send('forward %d' % cm)

    def back(self, cm):
        return self.send('back %d' % cm)

    def cw(self, degree):
        return self.send('cw %d' % degree)

    def ccw(self, degree):
        return self.send('ccw %d' % degree)


class TelloControl:
    def __init__(self):
        self._cmd = TelloCommand()

    def enter_command_mode(self):
        while True:
            # コマンドモード
            r = self._cmd.command()
            if r == 'ok':
                print("command response OK")
                break
            print("wait for command response...")

    def has_enough_battery(self):
        r = self._cmd.send('battery?')
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

    def terminate(self):
        self.streamoff()
        self.land()

    def status(self):
        t = self._cmd.status()
        return t

    def send(self, cmd):
        return self._cmd.send(cmd)

    def takeoff(self):
        return self._cmd.takeoff()

    def land(self):
        return self._cmd.land()

    def streamon(self):
        return self._cmd.streamon()

    def streamoff(self):
        return self._cmd.streamoff()

    def emergency(self):
        return self._cmd.emergency()

    def up(self, cm):
        return self._cmd.up(cm)

    def down(self, cm):
        return self._cmd.down(cm)

    def left(self, cm):
        return self._cmd.left(cm)

    def right(self, cm):
        return self._cmd.right(cm)

    def forward(self, cm):
        return self._cmd.forward(cm)

    def back(self, cm):
        return self._cmd.back(cm)

    def cw(self, degree):
        return self._cmd.cw(degree)

    def ccw(self, degree):
        return self._cmd.ccw(degree)


def main():
    ctrl = TelloControl()
    if ctrl.initialize() is False:
        exit()
    #ctrl.status()
    ctrl.send("takeoff")
    #ctrl.send("cw 180")
    #ctrl.send("ccw 180")
    ctrl.send("land")
    print("Drone Control Program : Start")


if __name__ == "__main__":
    main()
