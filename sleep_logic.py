import time
import upload

RATIO = 0.99
TARGET = 8 * 60  # 8 hours in minutes
sleep_debt = 0


def next_sleep_dep(previous, new_sleep):
  delta = dt()
  return (RATIO ** delta) * previous + delta * TARGET - new_sleep


previous_time = time.time()
SEC_PER_DAY = 60 * 60 * 24.0
def dt():
  global previous_time
  val = (time.time() - previous_time) / SEC_PER_DAY
  previous_time = time.time()
  return val


def sleep_dep_loop():
  global sleep_debt
  yield
  sleep_amount = 0
  sleep_debt = 0
  while True:
    sleep_debt = next_sleep_dep(sleep_debt, sleep_amount)
    sleep_amount = upload.duration_to_minutes((yield (sleep_debt)))


__loop = sleep_dep_loop()
next(__loop)
sleep_handler = __loop.send
