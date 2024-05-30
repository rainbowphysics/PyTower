import builtins
from collections import deque
import itertools
from typing import TYPE_CHECKING, Any, Callable, Generic, Iterable, Iterator, ParamSpec, Protocol, Reversible, Sequence, TypeAlias, TypeVar, TypeVarTuple, overload
import functools

P = ParamSpec("P")
E = ParamSpec("E")
IN = TypeVar("IN", contravariant=True)
OUT = TypeVar("OUT", covariant=True)

Ts = TypeVarTuple("Ts")
U = TypeVar('U')

class typed(Generic[*Ts, U]):
    def __new__(cls, f: Callable[[*Ts], U], /) -> Callable[[*Ts], U]:
        return f

class PipeFunc(Protocol[IN, OUT, P]):
    def __call__(self, iterable: IN, *args: P.args, **kwargs: P.kwargs) -> OUT: ...

class pipe(Generic[IN, OUT, P]):
    function: PipeFunc[IN, OUT, P]

    def __init__(self, function: PipeFunc[IN, OUT, P]):
        self.function = function
        functools.update_wrapper(self, function)

    def __ror__(self, other: IN) -> OUT:
        return self.function(other) # type: ignore

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> 'pipe[IN, OUT, E]':
        return pipe[IN, OUT, E](lambda iterable: self.function(iterable, *args, **kwargs)) # type: ignore

@pipe
def take(iterable: Iterable[IN], qte: int):
    "Yield qte of elements in the given iterable."
    for item in iterable:
        if qte > 0:
            qte -= 1
            yield item
        else:
            return


@pipe
def tail(iterable: Iterable[IN], qte: int):
    "Yield qte of elements in the given iterable."
    return deque(iterable, maxlen=qte)


@pipe
def skip(iterable: Iterable[IN], qte: int):
    "Skip qte elements in the given iterable, then yield others."
    for item in iterable:
        if qte == 0:
            yield item
        else:
            qte -= 1


@pipe
def dedup(iterable: Iterable[IN], key: Callable[[IN], Any]=lambda x: x):
    """Only yield unique items. Use a set to keep track of duplicate data."""
    seen = set[Any]()
    for item in iterable:
        dupkey = key(item)
        if dupkey not in seen:
            seen.add(dupkey)
            yield item


@pipe
def uniq(iterable: Iterable[IN], key: Callable[[IN], Any]=lambda x: x):
    """Deduplicate consecutive duplicate values."""
    iterator = iter(iterable)
    try:
        prev = next(iterator)
    except StopIteration:
        return
    yield prev
    prevkey = key(prev)
    for item in iterator:
        itemkey = key(item)
        if itemkey != prevkey:
            yield item
        prevkey = itemkey


@pipe
def permutations(iterable: Iterable[IN], r: int | None=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    for x in itertools.permutations(iterable, r):
        yield x


@pipe
def select(iterable: Iterable[IN], selector: Callable[[IN], OUT]):
    return builtins.map(selector, iterable)


@pipe
def where(iterable: Iterable[IN], predicate: Callable[[IN], Any]):
    return (x for x in iterable if predicate(x))


@pipe
def take_while(iterable: Iterable[IN], predicate: Callable[[IN], bool]):
    return itertools.takewhile(predicate, iterable)


@pipe
def skip_while(iterable: Iterable[IN], predicate: Callable[[IN], bool]):
    return itertools.dropwhile(predicate, iterable)

if TYPE_CHECKING:
    _T_contra = TypeVar("_T_contra", contravariant=True)
    class SupportsDunderLT(Protocol[_T_contra]):
        def __lt__(self, other: _T_contra, /) -> bool: ...

    class SupportsDunderGT(Protocol[_T_contra]):
        def __gt__(self, other: _T_contra, /) -> bool: ...

    SupportsRichComparison: TypeAlias = SupportsDunderLT[Any] | SupportsDunderGT[Any]
    SupportsRichComparisonT = TypeVar("SupportsRichComparisonT", bound=SupportsRichComparison)  # noqa: Y001
    TKey = TypeVar('TKey', bound=SupportsRichComparison)
@pipe
def groupby(iterable: Iterable[IN], keyfunc: Callable[[IN], TKey]) -> Iterator[tuple[TKey, Iterator[IN]]]:
    return itertools.groupby(sorted(iterable, key=keyfunc), keyfunc)


@overload
def sort(iterable: Iterable[SupportsRichComparisonT], key: None=None, reverse: bool=False) -> list[SupportsRichComparisonT]: ...
@overload
def sort(iterable: Iterable[IN], key: Callable[[IN], SupportsRichComparison], reverse: bool=False) -> list[IN]: ...
@pipe
def sort(iterable: Iterable[IN], key: Callable[[IN], SupportsRichComparison], reverse: bool=False):  # pylint: disable=redefined-outer-name
    return sorted(iterable, key=key, reverse=reverse)


@pipe
def reverse(iterable: Reversible[IN]):
    return reversed(iterable)

T = TypeVar('T')
@pipe
def t(iterable: Iterable[IN], y: T) -> Sequence[IN | T]:
    if hasattr(iterable, "__iter__") and not isinstance(iterable, str):
        return iterable + type(iterable)([y]) # type: ignore
    return [iterable, y] # type: ignore


@pipe
def transpose(iterable: Iterable[IN]):
    return list(zip(*iterable))


@pipe
def to_list(iterable: Iterable[IN]) -> list[IN]:
    return list(iterable)