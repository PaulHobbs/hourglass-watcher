import simplejson as json
import time
from upload import process_point


def conf():
  with open("conf.json", "r") as f:
    return json.load(f)


def next_sleep_dep(previous, new_sleep):
  c = conf()
  return (c['ratio'] ** dt()) * previous + (c['target'] - new_sleep)


previous_time = time.time()
SEC_PER_DAY = 60 * 60 * 24.0
def dt():
  val = (time.time() - previous_time) / SEC_PER_DAY
  global previous_time
  previous_time = time.time()
  return val


def sleep_dep_loop():
  sleep_amount = 0
  sleep_debt = 0
  while True:
    sleep_debt = next_sleep_dep(sleep_debt, sleep_amount)
    sleep_amount = (yield (sleep_debt))['duration']

sleep_handler = sleep_dep_loop()
