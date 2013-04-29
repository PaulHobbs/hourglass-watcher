from datetime import datetime, date, timedelta
from functools import partial
from itertools import chain
import contextlib, pickle
import json

import upload

HEIRARCHICAL_GOAL_POSTFIX = '-accum'


@contextlib.contextmanager
def load_unload(k, m):
  # maintain the set of seen points between runs.
  try:
    with open(k + ".db", "rb") as fp:
      m[k] = pickle.load(fp)
  except:
    pass

  def catch(e):
    with open(k + ".db", "wb") as fp:
      pickle.dump(m[k], fp)
    raise e

  try:
    yield
  except KeyboardInterrupt as e:
    catch(e)
  except Exception as e:
    catch(e)


get_hash = partial(json.dumps, sort_keys=True)

def heirarchal_goals():
  return set(g for g in upload.GOALS
             if g.endswith(HEIRARCHICAL_GOAL_POSTFIX))


def in_heirarchal_goal(datum):
  for g in heirarchal_goals():
    if HEIRARCHICAL_GOAL_POSTFIX in g:
      g_ = g[:-len(HEIRARCHICAL_GOAL_POSTFIX)]
      if datum['activity name'] == g_ or g_ in datum['hierarchy path']:
        return g


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
