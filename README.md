# m h  dom mon dow   command
0 8 * * * cd /home/stefandragicevic/telegram_bot/crypto && /home/stefandragicevic/telegram_bot/.venv/bin/python3 get_btc_data.py >> /home/stefandragicevic/telegram_bot/crypto/cron.log 2>&1
25 8 * * * cd /home/stefandragicevic/telegram_bot && /home/stefandragicevic/telegram_bot/.venv/bin/python3 main.py >> /home/stefandragicevic/telegram_bot/cron.log 2>&1