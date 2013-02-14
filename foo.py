#!/usr/bin/env python
from __future__ import print_function

import logging
from collections import deque

import taperecorder
from taperecorder import create_observer_cls
from taperecorder import Action, ReactingCall


class AssertingReaction(object):
    """
    Reaction class for testing.

    Creates a reaction object that uses TestCase assertions to expect a
    sequence of actions. Allows to customize each reaction with a callback.
    """

    def __init__(self):
        self.chain = deque()

    def add(self, action, callback):
        """
        Add a callback reaction to an expected action
        """
        self.chain.append((action, callback))

    def to(self, action):
        """
        Provide action with a reaction
        """
        print("Reacting to action %r" % (action,))
        try:
            assert len(self.chain) > 0, "Expected action chain empty!?!, got action %r" % (action,)
            expected_action, callback = self.chain.popleft()
            assert action == expected_action, "Action mismatch, expected %r, got %r" % (expected_action, action)
        except AssertionError as exc:
            print("Assertion error", exc)
            raise SystemExit()
        except:
            logging.exception("AssertingReaction.to() failed")
            raise
        else:
            print("Consumed action", action)
            return callback()


class Sentinel(object):
    pass


def main():
    taperecorder.use_real_repr = True 
    reaction = AssertingReaction()
    cls = create_observer_cls(reaction)
    obj = cls()
    reaction.add(
        Action('__get__', '__dir__', (obj, cls), {}),
        lambda: ReactingCall('__dir__', reaction))
    reaction.add(
        Action('__call__', '__dir__', (), {}),
        lambda: ['foo', 'bar', 'froz'])
    assert dir(obj) == sorted(['foo', 'bar', 'froz'])
    assert len(reaction.chain) == 0, "Not all actions used"


if __name__ == "__main__":
    main()
