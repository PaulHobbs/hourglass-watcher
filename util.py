from functools import partial
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
