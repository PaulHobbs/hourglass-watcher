import simplejson as json

def conf():
  with open("conf.json", "r") as f:
    return json.load(f)

def next_sleep_dep(previous, new_sleep):
  c = conf()
  return c['ratio'] * previous + (c['target'] - new_sleep)

current_sleep_dep = 0
