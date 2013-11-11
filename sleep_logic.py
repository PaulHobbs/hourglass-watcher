import time
import upload

RATIO = 0.95
TARGET = 8.5 * 60  # hours in minutes
sleep_debt = 0


def next_sleep_dep(previous, new_sleep):
  delta = dt()
  debt = (RATIO ** delta) * previous + delta * TARGET - new_sleep
  return max(debt, 0)


previous_time = time.time()
SEC_PER_DAY = 60 * 60 * 24.0


def dt():
  global previous_time
  val = (time.time() - previous_time) / SEC_PER_DAY
  previous_time = time.time()
  return val


def sleep_dep_loop():
  global sleep_debt
  sleep_amount = 0
  yield
  while True:
    sleep_debt = next_sleep_dep(sleep_debt, sleep_amount)
    sleep_amount = upload.duration_to_minutes((yield (sleep_debt)))


__loop = sleep_dep_loop()
next(__loop)
sleep_handler = __loop.send


def matches_sleep(datum):
  return datum['activity name'] == 'sleep' or 'sleep' in datum['hierarchy path']
