from typing import Generic, Literal, Iterable, Iterator, overload

class _IndexMeta(type):

  def __new__(cls, __name: str, __bases: tuple[type, ...], __namespace: dict[str, any], **kwds):
    
    new = super().__new__(cls, __name, __bases, __namespace, **kwds)

    if any(issubclass(b, Generic) for b in new.mro()):
      raise ValueError(f"Index type is not \"Generic\" subclass")

    index_name_map: dict[int, str] = dict(getattr(new, "_index_name_map", {}))
    setattr(new, "_index_name_map", index_name_map)

    for k, v in __namespace.items():

      if k[0] == "_" or not k.isupper(): continue

      if v in index_name_map:
        raise ValueError(f"{v} is already used in \"{__name}\" class.")

      index_name_map[v] = k
    
    for k, v in new.__annotations__.items():

      if k[0] == "_" or not k.isupper(): continue

      if not v.__dict__.get("__origin__", None) == Literal: continue
      if not v.__args__ or not isinstance(init_value := v.__args__[0], int): continue
      if isinstance(getattr(new, k, None), int): continue

      if init_value in index_name_map:
        raise ValueError(f"{init_value} is already used in \"{__name}\" class.")

      index_name_map[init_value] = k
      setattr(new, k, init_value)

    return new
  
  def __init__(self, __name: str, __bases: tuple[type, ...], __namespace: dict[str, any], **kwds):
    super().__init__(__name, __bases, __namespace, **kwds)
    self._index_name_map: dict[int, str]
  def __iter__(self):
    return iter(self._index_name_map.values())
  def __len__(self):
    return len(self._index_name_map)
  def __contains__(self, __key):
    if isinstance(__key, int):
      return __key in self._index_name_map
    elif isinstance(__key, str):
      return __key in self._index_name_map.values()
    else:
      return False
  @overload
  def __getitem__(self, __key: int) -> str: ...
  @overload
  def __getitem__(self, __key: Iterable[int]) -> Iterator[str]: ...
  def __getitem__(self, __key):
    if isinstance(__key, int):
      return self._index_name_map[__key]
    elif isinstance(__key, Iterable):
      return (self._index_name_map[k] for k in __key)
    else: raise KeyError(f"only int or Iterable[int] allowed. ({__key.__class__})")

class Index(metaclass=_IndexMeta):
  "インデックスクラス"

