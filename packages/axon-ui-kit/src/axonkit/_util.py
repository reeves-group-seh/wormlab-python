# local
import axon

# wrap a value that may be reactive, or may not be
type Value[T] = axon.Atom[T] | T


# convert a value to an atom
def as_atom[T](value: Value[T]) -> axon.Atom[T]:
    return value if isinstance(value, axon.Atom) else axon.Atom(value)
