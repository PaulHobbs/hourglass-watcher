#! /usr/bin/python2.7
import csv
import os
import sys
import subprocess

from pprint import pprint
from time import sleep
from operator import itemgetter
from itertools import count, chain
from datetime import datetime, date, timedelta
from time import mktime
import simplejson as json

ext = subprocess.check_output

USER = None
AUTH_TOKEN = None

seen = set()

def root():
  return 'https://www.beeminder.com/api/v1/users/' + USER

def token():
  return 'auth_token=%s' % AUTH_TOKEN


def string_time_to_unix(string_time):
  h, m, s, am_pm = chain.from_iterable(
      map(lambda part: part.split(),
          string_time.split(':')))

  h,m,s = map(int, (h,m,s))

  today = date.today()
  extra = timedelta(0,0,0,0,0,
                    12 if am_pm.lower() == "pm" and h != 12
                    else 0)
  then = datetime(today.year, today.month, today.day, h, m, s, 0) + extra
  return mktime(then.timetuple())  # convert to unix timestamp


def process_point(datum, goal):

  # Don't tell Beeminder twice about the same data point.
  hash_ = json.dumps(datum, sort_keys = True)
  if hash_ in seen:
    return
  seen.add(hash_)

  h,m,s = datum['duration'].split(':')
  dur = int(h)*60 + int(m)  # round off seconds because of tracking overhead.
  timestamp = datum['start time']

  comment = datum['note']
  if datum['tags']:
    comment += "  tags:" + datum['tags']

  put_point(timestamp, dur, goal, comment)


def put_point(timestamp, dur, goal, note):
  print timestamp, dur, goal


  success = False
  while not success:
    try:
      args = ['http', 'POST', root() + '/goals/' + goal + '/datapoints.json',
                  'timestamp=%d' % timestamp,
                  'value=%d' % dur,
                  "comment='%s'" % note,
                  token()]
      print "args: "
      pprint(args)
      result = ext(args)
      print "Success!  Result:"
      print
      print result
      print
      success = True
    except Exception as e:
      print "Warning: POSTing failed with exception: ", e
      sleep(10)


def process_file(fname):
  data = []
  with open(fname, 'r') as fp:
    rdr = csv.reader(fp)
    first_row = rdr.next()
    print "Column names: ", first_row
    get = dict(zip(first_row,
                   map(itemgetter, range(len(first_row)))))

    for row in csv.reader(fp):
      print "read row: ", row
      datum = {}
      for k, a in get.iteritems():
        datum[k] = a(row)

      data.append(datum)

  for datum in data:
    activity = datum['activity name']
    datum['start time'] = string_time_to_unix(datum['start time'])
    if activity in GOALS:
      process_point(datum, activity)


def main():
  path_to_watch = "."
  before = set(os.listdir(path_to_watch))

  global AUTH_TOKEN, USER
  USER, AUTH_TOKEN = sys.argv[1:3]

  while 1:
    sleep(60)
    after = set(os.listdir('.'))
    added = [name for name in after - before
             if '_logs_' in name]

    if added: print "Added: ", ", ".join (added)

    update_goals()
    map(process_file, added)

    before = after


def update_goals():
  global GOALS

  try:
    result = ext(["http", 'GET', root() + '.json',
                  token()])
    GOALS = json.loads(result)['goals']
  except Exception as e:
    print "Warning: goal-getting failed!"
    print e


if __name__ == '__main__':
  # maintain the set of seen points between runs.
  try:
    with open("seen.db", "r") as fp:
      seen = pickle.load(fp)
  except IOError:
    pass

  try:
    main()
  except:
    with open("seen.db", "w") as fp:
      pickle.dump(seen, fp)
    raise
