# modem_sms_to_telegram
Python script for Orange Pi. The script sends you incoming SMS via telegram.


SCRIPT IS NOT COMPATIBLE WITH *MINICOM* PROGRAM

The following data must be entered into the script:
- ser.port ( сommand to display device list 'ls -l /dev/ttyS*' )
- bot_id ( you need to create your bot in @BotFather and enter its id )
- user_id ( your telegram id, you can get it from the bot @userinfobot )

The bot will send a message only to you, according to your id
