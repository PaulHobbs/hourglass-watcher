import json
import subprocess

from pprint import pprint
from time import sleep

GOALS = None
seen = set()

def ext(*args):
 return subprocess.check_output(*args).decode('utf-8')

USER = None
AUTH_TOKEN = None

def root():
  return 'https://www.beeminder.com/api/v1/users/' + USER


def token():
  return 'auth_token=%s' % AUTH_TOKEN


def duration_to_minutes(datum):
  if not datum['duration']:
    return 0

  # is it numeric or a number string?
  try:
    return int(datum['duration'])
  except ValueError:
    pass

  # parse a h:m:s or m:s
  h = 0
  try:
    h,m,_ = datum['duration'].split(':')
  except ValueError:
    m,_ = datum['duration'].split(':')
  return int(h)*60 + int(m)  # round off seconds because of tracking overhead.


def process_point(datum, goal):
  """ Upload the duration to the beeminder goal. """

  # Don't tell Beeminder twice about the same data point.
  hash_ = json.dumps(datum, sort_keys=True)
  if hash_ in seen:
    return

  comment = datum['note']
  if datum['tags']:
    comment += "  tags:" + datum['tags']

  put_point(datum['start time'], duration_to_minutes(datum), goal, comment)
  seen.add(hash_)


def put_point(timestamp, dur, goal, note):
  print (timestamp, dur, goal)


  success = False
  while not success:
    try:
      args = ['http', 'POST', root() + '/goals/' + goal + '/datapoints.json',
                  'timestamp=%d' % timestamp,
                  'value=%d' % dur,
                  "comment='%s'" % note,
                  token()]
      print ("args: ")
      pprint(args)
      result = ext(args)
      print ("Success!  Result:")
      print ()
      print (result)

      success = True
    except Exception as e:
      print ("Warning: POSTing failed with exception: ", e)
      sleep(10)




def update_goals():
  global GOALS

  try:
    result = ext(["http", 'GET', root() + '.json',
                  token()])
    GOALS = json.loads(result)['goals']
  except Exception as e:
    print ("Warning: goal-getting failed!")
    print (e)
