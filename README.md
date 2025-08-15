Cron jobs should be created like this:

# m h  dom mon dow   command
20 8 * * * cd /home/stefandragicevic/telegram_bot && /home/stefandragicevic/telegram_bot/.venv/bin/python3 fetch_all_data.py >> /home/stefandragicevic/telegram_bot/cron.log 2>&1
25 8 * * * cd /home/stefandragicevic/telegram_bot && /home/stefandragicevic/telegram_bot/.venv/bin/python3 crypto_main.py >> /home/stefandragicevic/telegram_bot/cron.log 2>&1
20 20 * * * cd /home/stefandragicevic/telegram_bot && /home/stefandragicevic/telegram_bot/.venv/bin/python3 quote_of_the_day.py >> /home/stefandragicevic/telegram_bot/cron.log 2>&1
2 20 * * * cd /home/stefandragicevic/telegram_bot && /home/stefandragicevic/telegram_bot/.venv/bin/python3 business_psychology.py >> /home/stefandragicevic/telegram_bot/cron.log 2>&1