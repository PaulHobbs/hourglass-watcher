#! /usr/local/bin/python3
import csv
import os
import sys

from operator import itemgetter
from sleep_logic import sleep_handler, matches_sleep
from util import load_unload, get_hash, in_heirarchal_goal, HEIRARCHICAL_GOAL_POSTFIX, string_time_to_unix
from time import sleep

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

    def process(activity_name, datum=datum):
      upload.process_point(datum, activity_name)
      print ("adding hash: ", hash_)
      seen.add(hash_)

    heirarchical_activity = in_heirarchal_goal(datum)
    if heirarchical_activity:
      datum_ = dict(datum,
                    note='%s  -- (%s)' % (datum['note'], datum['activity name']))
      process(heirarchical_activity, datum_)

    if matches_sleep(datum):
      activity = 'sleepdebt'
      datum['duration'] = sleep_handler(datum)
      process(activity)

    elif activity in upload.GOALS:
      process(activity)


if __name__ == '__main__':
  with load_unload("seen", globals()):
    with load_unload("previous_time", sleep_logic.__dict__):
      main()
