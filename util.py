from functools import partial
import contextlib, pickle
import json

import upload

HEIRARCHAL_GOAL_POSTFIX = '-accum'


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
  return set(g
             for g in upload.GOALS
             if g.endswith(HEIRARCHAL_GOAL_POSTFIX))


def in_heirarchal_goal(datum):
  return any(datum['activity name'] == g + HEIRARCHAL_GOAL_POSTFIX
             or g in datum['hierarchy path']
             for g in heirarchal_goals())
