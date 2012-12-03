import contextlib, pickle
import json


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


def get_hash(datum):
  return json.dumps(datum, sort_keys=True)
