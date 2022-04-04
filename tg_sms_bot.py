import telebot
from time import sleep
import serial
import sqlite3

ser = serial.Serial()

ser.port = '/dev/ttyUSB0'
# ser.baudrate = 9600 for old modem
ser.baudrate = 115200
ser.timeout = 1
bot_id = ""
user_id = 

ser.open()

con = sqlite3.connect('sms_history.db')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS sms
               (date text, sender text, message text)''')
con.commit()


def send_at(at_command, time_slp=1):
    ser.write(str.encode('{}\r\n'.format(at_command)))
    sleep(time_slp)

def decode_sms_text(txt):
    kkl = ''.join(chr(int(txt[i:i+4], 16)) for i in range(0, len(txt), 4)) 
    return kkl

send_at('AT+CSCS="UCS2"',1)
send_at('AT+CMGF=1',1)
send_at('AT+CPMS="ME","SM","ME"',1)

bot = telebot.TeleBot(bot_id)

def main(message):
    send_at('AT+CMGF=1',0)
    send_at('AT+CMGL="ALL"')
    at_resp = ser.readlines()
    tg_msg = ''
    end_tg_msg = ''
    start_sms=0
    for row_resp in at_resp:
        if row_resp[0:6]==b'+CMGL:' and row_resp != b'+CPMS: 0,23,2,5,0,23\r\n':
            start_sms=1
            sms_header = row_resp.decode("utf-8").split(",")
            for d in range(len(sms_header)):
                sms_header[d] = sms_header[d].replace('"', '')
                sms_header[d] = sms_header[d].replace('\r\n', '')
            if sms_header[2][0:1] != '+' or sms_header[2][0:1] != '8' or sms_header[2][0:1] != '7' :
                sms_header[2] = decode_sms_text(sms_header[2][:len(sms_header[2])-2])
            tg_msg = tg_msg + '<b>From</b>: ' + str(sms_header[2]) + '\r\n'
            tg_msg = tg_msg + '<code>' + str(sms_header[4]) + '  ' + str(sms_header[5]) + '</code>\r\n'
        elif start_sms==1 and row_resp[0:6]!=b'+CMGL:':
            start_sms=0
            end_tg_msg = tg_msg + str(decode_sms_text(row_resp[:len(row_resp)-2]) ) + '\r\n'
            tg_msg = ''
            cur = con.cursor()
            cur.execute("INSERT INTO sms VALUES (?, ?, ?)", (str(sms_header[4]) + '  ' + str(sms_header[5]), str(sms_header[2]), str(decode_sms_text(row_resp[:len(row_resp)-2]) ) ) )
            con.commit()
            
        elif row_resp[0:3] != b'AT+' and row_resp[0:2] != b'OK' and row_resp != b'\r\n' and row_resp != b'+CPMS: 0,23,2,5,0,23\r\n' :
            start_sms=0
            end_tg_msg = tg_msg + row_resp.decode("utf-8")
            tg_msg = ''

    if end_tg_msg != '' :
        bot.send_message(user_id, end_tg_msg, parse_mode="HTML")
        send_at('AT+CMGD=2,1')
        # send_at('AT+CMGD=4')



if __name__ == '__main__':
    while True:
        main('')
