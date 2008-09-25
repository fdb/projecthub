import os.path
import unittest
from dmigrations.exceptions import *

class WarningsMocker(object):
  def __init__(self):
    self.warnings = []
  def __call__(self, warning):
    self.warnings.append(warning)

class TestCase(unittest.TestCase):
  """
  Common code, and Pythonic (underscored) names support, instead of ugly javaCamelCase.
  """
  def assert_attrs(self, obj, **kwargs):
    for key in sorted(kwargs.keys()):
      expected = kwargs[key]
      actual = getattr(obj, key)
      self.assert_equal(expected, actual, u"Object's %s expected to be `%s', is `%s' instead" % (key, expected, actual))

  def assert_raises(self, expected_exception_class, code):
    try:
      code()
      self.assert_(False, u"Exception %s expected, but no exception raised" % expected_exception_class)
    except Exception, e:
      if isinstance(e, expected_exception_class):
        self.assert_(True)
      else:
        raise # Assert false or raise an error is better ?
        self.assert_(False, u"Exception %s expected, `%s' exception raised instead" % (expected_exception_class, e))

  def assert_equal(self, *args, **kwargs):
    self.assertEqual(*args, **kwargs)

  def setUp(self):
    self.mock_migrations_dir = os.path.join(os.path.dirname(__file__), "mock_migrations_dir")
    self.set_up()
  
  def set_up(self):
    pass

  def tearDown(self):
    self.tear_down()
  
  def tear_down(self):
    pass
