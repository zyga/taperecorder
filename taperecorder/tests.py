from __future__ import print_function

from unittest import TestCase
from collections import deque

from taperecorder import create_observer_cls
from taperecorder import Action, ReactingCall


def throw(exc):
    """
    Helper function to make raise an expression, not a statement
    """
    raise exc


class AssertingReaction(object):
    """
    Reaction class for testing.

    Creates a reaction object that uses TestCase assertions to expect a
    sequence of actions. Allows to customize each reaction with a callback.
    """

    def __init__(self, testcase, auto_descriptors=False):
        self.testcase = testcase
        self.chain = deque()
        self.auto_descriptors = auto_descriptors

    def add(self, action, callback):
        """
        Add a callback reaction to an expected action
        """
        self.chain.append((action, callback))

    def to(self, action):
        """
        Provide action with a reaction
        """
        # If auto_descriptors are enabled then service all descriptor calls
        # automatically without cluttering the expected action chain.
        if self.auto_descriptors:
            if action.origin in ('__get__', '__set__', '__delete__'):
                return ReactingCall(action.name, self)
        # Pop the next item from the expected action / reaction chain
        expected_action, callback = self.chain.popleft()
        # Do some fine-tuned testing for easier error messages
        self.testcase.assertEqual(action.origin, expected_action.origin)
        self.testcase.assertEqual(action.name, expected_action.name)
        self.testcase.assertEqual(action.args, expected_action.args)
        self.testcase.assertEqual(action.kwargs, expected_action.kwargs)
        # But test everything in case action gets changed
        self.testcase.assertEqual(action, expected_action)
        # Return what the callback did
        return callback()


class ObserverTests(TestCase):

    def setUp(self):
        # The asserting reaction instance.
        # We feed this puppy with assertion data, it checks things
        # as we are using the object created later.
        self.reaction = AssertingReaction(self)
        # Automatically service descriptor calls
        self.reaction.auto_descriptors = True
        # The observer class that talks to the reaction instance above We don't
        # use the class in any way but we need a per-reaction-instance class
        # as we need methods on the metaclass being able to see the reaction
        # instance.
        self.cls = create_observer_cls(self.reaction)
        # Spawn the observer, __all__ interaction on the observer gets
        # delegated to the reaction class.
        self.obj = self.cls()

    def tearDown(self):
        # As a part of the test process, check that we've used all of the
        # reactions. If we didn't then the test did not really do what was
        # assumed.
        self.assertEqual(len(self.reaction.chain), 0,
                         "Not all reactions were used")

    def test_str(self):
        # Expect the method call on __str__()
        self.reaction.add(
            action=Action('__call__', '__str__', (), {}),
            callback=lambda: "foo")
        # Make sure we got it right
        self.assertEqual(str(self.obj), "foo")

    def test_repr(self):
        # Expect the method call on __repr__()
        self.reaction.add(
            action=Action('__call__', '__repr__', (), {}),
            callback=lambda: "<foo>")
        # Make sure we got it right
        self.assertEqual(repr(self.obj), "<foo>")

    def test_setattr(self):
        # Expect the method call on __setattr__('foo', 5)
        self.reaction.add(
            action=Action('__call__', '__setattr__', ('foo', 5), {}),
            callback=lambda: None)
        # Make sure we got it right
        self.obj.foo = 5

    def test_getattr(self):
        # Expect the method call __getattr__('foo')
        self.reaction.add(
            action=Action('__call__', '__getattr__', ('foo',), {}),
            callback=lambda: 5)
        # Make sure we got it right
        self.assertEqual(self.obj.foo, 5)

    def test_delattr(self):
        # Expect the method call __getattr__('foo')
        self.reaction.add(
            action=Action('__call__', '__delattr__', ('foo',), {}),
            callback=lambda: 5)
        # Make sure we got it right
        del self.obj.foo

    def test_method_calls(self):
        # Expect the method call on __getattr__('foo')
        # This will produce a ReactingCall object being returned
        self.reaction.add(
            action=Action('__call__', '__getattr__', ('foo',), {}),
            callback=lambda: ReactingCall('foo', self.reaction))
        # Then expect the method call on foo(1, arg=6)
        self.reaction.add(
            action=Action('__call__', 'foo', (1,), {"arg": 6}),
            callback=lambda: 5)
        # Make sure we got it right
        self.assertEqual(self.obj.foo(1, arg=6), 5)

    def test_lt(self):
        # Expect the method call __lt__(10)
        self.reaction.add(
            action=Action('__call__', '__lt__', (10,), {}),
            callback=lambda: True)
        # Make sure we got it right
        self.assertTrue(self.obj < 10)

    def test_le(self):
        # Expect the method call __le__(10)
        self.reaction.add(
            action=Action('__call__', '__le__', (10,), {}),
            callback=lambda: True)
        # Make sure we got it right
        self.assertTrue(self.obj <= 10)

    def test_eq(self):
        # Expect the method call __le__(10)
        self.reaction.add(
            action=Action('__call__', '__eq__', (10,), {}),
            callback=lambda: True)
        # Make sure we got it right
        self.assertTrue(self.obj == 10)

    def test_ne(self):
        # Expect the method call __ne__(10)
        self.reaction.add(
            action=Action('__call__', '__ne__', (10,), {}),
            callback=lambda: True)
        # Make sure we got it right
        self.assertTrue(self.obj != 10)

    def test_gt(self):
        # Expect the method call __gt__(10)
        self.reaction.add(
            action=Action('__call__', '__gt__', (10,), {}),
            callback=lambda: True)
        # Make sure we got it right
        self.assertTrue(self.obj > 10)

    def test_ge(self):
        # Expect the method call __ge__(10)
        self.reaction.add(
            action=Action('__call__', '__ge__', (10,), {}),
            callback=lambda: True)
        # Make sure we got it right
        self.assertTrue(self.obj >= 10)

    def test_le_via_cmp(self):
        # Disable automatic descriptors as we want to be able to change
        # default behavior.
        self.reaction.auto_descriptors = False
        # First expect the 'get' descriptor access on __le__
        # This must raise AttributeError for python to keep searching
        self.reaction.add(
            action=Action('__get__', '__le__', (self.obj, self.cls), {}),
            callback=lambda: throw(AttributeError))
        # Then expect the 'get' descriptor access on __cmp___
        # This will produce a ReactingCall object being returned
        self.reaction.add(
            action=Action('__get__', '__cmp__', (self.obj, self.cls), {}),
            callback=lambda: ReactingCall('__cmp__', self.reaction))
        # Expect the method call __cmp__(10)
        self.reaction.add(
            action=Action('__call__', '__cmp__', (10,), {}),
            callback=lambda: -1)
        # Make sure we got it right
        self.assertTrue(self.obj <= 10)

    def test_getitem(self):
        # Expect the method call __getitem__(10)
        self.reaction.add(
            action=Action('__call__', '__getitem__', (10,), {}),
            callback=lambda: "foo")
        # Make sure we got it right
        self.assertEqual(self.obj[10], "foo")

    def test_setitem(self):
        # Expect the method call __setitem__(10)
        self.reaction.add(
            action=Action('__call__', '__setitem__', (10, "foo"), {}),
            callback=lambda: None)
        # Make sure we got it right
        self.obj[10] = "foo"

    def test_delitem(self):
        # Expect the method call __delitem__(10)
        self.reaction.add(
            action=Action('__call__', '__delitem__', (10,), {}),
            callback=lambda: None)
        # Make sure we got it right
        del self.obj[10]

    def test_isinstance(self):
        # Expect a call to __instancecheck__ to see if 'foo'
        # is an instance of our observer class
        self.reaction.add(
            action=Action('__instancecheck__', None, ('foo',), {}),
            callback=lambda: True)
        # Make sure we got it right
        self.assertTrue(isinstance('foo', self.cls))

    def test_issubclass(self):
        # Expect a call to __subclasscheck__ to see if 'foo'
        # is a subclass of our observer class
        self.reaction.add(
            action=Action('__subclasscheck__', None, ('foo',), {}),
            callback=lambda: True)
        # Make sure we got it right
        self.assertTrue(issubclass('foo', self.cls))

    def test_dir_contents(self):
        # Expect the method call __dir__
        self.reaction.add(
            Action('__call__', '__dir__', (), {}),
            lambda: ['b', 'c', 'a'])
        # Make sure we got it right.
        # Caveat: python sorts the result internally
        self.assertEqual(dir(self.obj), ['a', 'b', 'c'])
