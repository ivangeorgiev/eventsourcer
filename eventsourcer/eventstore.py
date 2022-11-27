from abc import abstractmethod
from collections.abc import Iterable
from typing import Generic, TypeVar

T = TypeVar("T")
TStored = TypeVar("TStored")


class Event:
    pass


class Encoder(Generic[T, TStored]):
    @abstractmethod
    def encode(self, obj: T) -> TStored:
        """Encode application object to stored object"""


class Decoder(Generic[TStored, T]):
    @abstractmethod
    def decode(self, obj: TStored) -> T:
        """Decode stored object into application object"""


class Transcoder(Encoder[T, TStored], Decoder[TStored, T], Generic[T, TStored]):
    pass


class Query(Generic[TStored]):
    @abstractmethod
    def execute(self) -> Iterable[TStored]:
        """Execute the query and return a sequence of results"""


class Insert(Generic[TStored]):
    @abstractmethod
    def insert(self, sequence: Iterable[TStored]):
        """Insert given sequence into the store"""


class AbstractStore(Generic[T, TStored]):
    transcoder: Transcoder[T, TStored]
    query: Query[TStored]
    insert: Insert[TStored]

    def get(self, sequence_id: str) -> Iterable[T]:
        return map(self.transcoder.decode, self.query.execute(sequence_id))

    def append(self, sequence: Iterable[T]):
        self.insert(map(self.transcoder.encode, sequence))
