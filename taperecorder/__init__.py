from __future__ import print_function

from collections import namedtuple

# Action encapsulates the basic python interaction -- a method call.
# This simple class captures a description of those arguments.
Action = namedtuple("Action", "origin name args kwargs")

# If set to True, __repr__ will show the true identity of the Observer objects
use_real_repr = False


class ReactingDescriptor(object):
    """
    Descriptor object that asks for the reaction
    """

    def __init__(self, name, reaction):
        self.name = name
        self.reaction = reaction

    def __get__(self, instance, owner):
        action = Action('__get__', self.name, (instance, owner), {})
        return self.reaction.to(action)

    def __set__(self, instance, value):
        action = Action('__set__', self.name, (instance, value), {})
        return self.reaction.to(action)

    def __delete__(self, instance):
        action = Action('__delete__', self.name, (instance,), {})
        return self.reaction.to(action)


class ReprReactingDescriptor(ReactingDescriptor):

    def __init__(self, reaction):
        super(ReprReactingDescriptor, self).__init__('__repr__', reaction)

    def __get__(self, instance, owner):
        if use_real_repr:
            return lambda: "<%s instance at %#0x>" % (owner.__name__, id(instance))
        else:
            return super(ReprReactingDescriptor, self).__get__(instance, owner)


class ReactingCall(object):
    """
    Callable object that asks for the reaction
    """

    def __init__(self, name, reaction):
        self.name = name
        self.reaction = reaction

    def __call__(self, *args, **kwargs):
        action = Action('__call__', self.name, args, kwargs)
        return self.reaction.to(action)


def create_observer_cls(reaction):
    """
    Create an observer type.

    The observer will relay any and all actions to the reaction object.
    """
    # Create a metaclass and a class with the 'reaction' variable in lexical
    # scoping. This way we can use it to create ReactingDescriptors
    class ObserverMeta(type):

        special_methods = (
            # Str and repr
            # '__repr__', # NOTE: __repr__ uses ReprReactinDescriptor
            '__str__',
            # Rich comparison methods
            '__lt__',
            '__le__',
            '__eq__',
            '__ne__',
            '__gt__',
            '__ge__',
            # Legacy comparison method
            '__cmp__',
            # Hashing
            '__hash__',
            # Boolean
            '__nonzero__',
            # Unicode str
            '__unicode__',
            # Attribute access
            '__getattr__',
            '__setattr__',
            '__delattr__',
            # Descriptors
            '__get__',
            '__set__',
            '__delete__',
            # Callable objects
            '__call__',
            # Container types
            '__len__',
            '__getitem__',
            '__setitem__',
            '__delitem__',
            '__iter__',
            '__reversed__',
            '__contains__',
            # Slice methods
            '__getslice__',
            '__setslice__',
            '__delslice__',
            # Numeric methods
            '__add__',
            '__sub__',
            '__mul__',
            '__div__',
            '__truediv__',
            '__floordiv__',
            '__mod__',
            '__divmod__',
            '__pow__',
            '__lshift__',
            '__rshift__',
            '__and__',
            '__xor__',
            '__or__',
            # reverse numeric methods
            '__radd__',
            '__rsub__',
            '__rmul__',
            '__rdiv__',
            '__rtruediv__',
            '__rfloordiv__',
            '__rmod__',
            '__rdivmod__',
            '__rpow__',
            '__rlshift__',
            '__rrshift__',
            '__rand__',
            '__rxor__',
            '__ror__',
            # augmented assignment methods
            '__iadd__',
            '__isub__',
            '__imul__',
            '__idiv__',
            '__itruediv__',
            '__ifloordiv__',
            '__imod__',
            '__idivmod__',
            '__ipow__',
            '__ilshift__',
            '__irshift__',
            '__iand__',
            '__ixor__',
            '__ior__',
            # unary operators
            '__neg__',
            '__pos__',
            '__abs__',
            '__invert__',
            # conversions and coertions
            '__complex__',
            '__int__',
            '__long__',
            '__float__',
            '__oct__',
            '__hex__',
            '__index__',
            '__coerce__',
            # contextmanagers
            '__enter__',
            '__exit__',
            # XXX:
            '__class__',
            '__dict__',
            '__dir__',
        )

        def __new__(mcls, name, bases, namespace):
            for func in mcls.special_methods:
                namespace[func] = ReactingDescriptor(func, reaction)
            namespace['__repr__'] = ReprReactingDescriptor(reaction)
            return type.__new__(mcls, name, bases, namespace)

        def __instancecheck__(cls, instance):
            action = Action('__instancecheck__', None, (instance,), {})
            return reaction.to(action)

        def __subclasscheck__(cls, subclass):
            action = Action('__subclasscheck__', None, (subclass,), {})
            return reaction.to(action)

    class Observer(object):

        __metaclass__ = ObserverMeta

    return Observer
