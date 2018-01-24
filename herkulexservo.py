import serial

class Servo:
    def __init__(self, port, baudrate, servoID):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        self.servoID = servoID
    
    def send_cmd(self, cmd, data):
        packetsize = 7 + len(data)
        checksum1 = packetsize ^ self.servoID ^ cmd
        for byte in data:
            checksum1 = checksum1 ^ byte
        checksum1 = checksum1&0xFE
        checksum2 = (~checksum1)&0xFE
        packet = [0xFF, 0xFF, packetsize, self.servoID, cmd, checksum1, checksum2]
        for byte in data:
            packet.append(byte)
        self.ser.write(serial.to_bytes(packet))

    def read_data(self, size=10):
        rxdata = self.ser.read(size)
        return [ord(b) for b in rxdata]

    def stat(self):
        self.send_cmd(0x07, [])

    def torque_on(self):
        self.send_cmd(0x03, [0x34, 0x01, 0x60])

    def move_to_angle(self, angle): # recommended range is within 0 - 300 deg
        position = int(angle/0.325 + 512)
        pos_LSB = position & 0xFF
        pos_MSB = (position & 0xFF00) >> 8
        led = 0 # green*4 + blue*8 + red*16
        playtime = 0x3C # execution time
        self.send_cmd(0x05, [pos_LSB, pos_MSB, led, self.servoID, playtime])

    def reboot(self):
        self.send_cmd(0x09,[])

    def close(self):
        self.ser.close()
