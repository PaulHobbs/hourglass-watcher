#! /usr/local/bin/python3
import csv
import os
import sys

from datetime import datetime, date, timedelta
from itertools import chain
from operator import itemgetter
from sleep_logic import sleep_handler, matches_sleep
from util import load_unload, get_hash, in_heirarchal_goal
from time import mktime, sleep

import upload, sleep_logic

seen = set()

def main():
  path_to_watch = "."
  before = set(os.listdir(path_to_watch))

  upload.USER, upload.AUTH_TOKEN = sys.argv[1:3]

  if len(sys.argv) > 3:
    sleep_logic.sleep_debt = int(sys.argv[3])

  while 1:
    after = set(os.listdir('.'))
    added = [name for name in after - before
             if '_logs_' in name]

    if added:
      print ("Added: ", ", ".join (added))
      upload.update_goals()
    list(map(process_file, added))

    before = after
    sleep(7)


def process_file(fname):
  data = []
  with open(fname, 'r') as fp:
    rdr = csv.reader(fp)
    first_row = next(rdr)
    print ("Column names: ", first_row)
    get = dict(zip(first_row,
                   map(itemgetter, range(len(first_row)))))

    for row in csv.reader(fp):
      print ("read row: ", row)
      datum = {}
      for k, a in get.items():
        datum[k] = a(row)

      data.append(datum)

  for datum in data:
    hash_ = get_hash(datum)
    if hash_ in seen:
      print ("Skipping ", datum)
      continue

    activity = datum['activity name']
    datum['start time'] = string_time_to_unix(datum['start time'])

    heirarchy_goal = False
    if in_heirarchal_goal(datum):
      heirarchy_goal = True

    if matches_sleep(datum):
      activity = 'sleepdebt'
      datum['duration'] = sleep_handler(datum)
      heirarchy_goal = True

    if activity in upload.GOALS or heirarchy_goal:
      upload.process_point(datum, activity)
      print ("adding hash: ", get_hash(datum))
      seen.add(hash_)


def string_time_to_unix(string_time):
  hms = chain.from_iterable(
      map(lambda part: part.split(),
          string_time.split(':')))

  # handle 24 hour time as always AM
  hms = list(hms)
  if len(hms) == 3:
    hms.append('am')

  h,m,s,am_pm = hms
  h,m,s = map(int, (h,m,s))

  today = date.today()
  extra = timedelta(0,0,0,0,0, 12 if am_pm.lower() == "pm" and h != 12 else 0)
  then = datetime(today.year, today.month, today.day, h, m, s, 0) + extra
  return mktime(then.timetuple())  # return unix timestamp


if __name__ == '__main__':
  with load_unload("seen", globals()):
    with load_unload("previous_time", sleep_logic.__dict__):
      main()
