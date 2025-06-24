import json
import re
import traceback
from collections.abc import ItemsView, KeysView, ValuesView
from typing import Any, Iterator, Optional, cast

from base.log import logger


class _localStore:
    """
    A local file store.
    """

    def __init__(self, filepath: str, default: object) -> None:
        self.filepath = filepath
        self.default = default
        self.load()

    def load(self) -> None:
        """
        Load data from file.
        """
        try:
            with open(self.filepath, 'r') as f:
                self.data = json.load(f)
        except Exception as e:
            logger.warning(
                f'Failed to load data, use default. {self.filepath}, {e}')
            logger.debug(traceback.format_exc())
            self.data = self.default
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f)

    def __dump_check(self, format=True) -> bool:
        """
        Check if the data can be dumped.
        :param format: format json
        :return: True if the data can be dumped, False otherwise
        """
        try:
            if format:  # format json
                json.dumps(self.data,
                           ensure_ascii=False, sort_keys=True, indent=4, default=str)
            else:
                json.dumps(self.data, default=str)
            return True
        except Exception as e:
            logger.warning(f'Failed to dump data. {self.filepath}, {e}')
            logger.debug(traceback.format_exc())
            return False

    def dump(self, format=True) -> None:
        """
        Dump data to file.
        :param format: format json
        """
        if not self.__dump_check(format):  # check if the data can be dumped
            return
        try:
            with open(self.filepath, 'w') as f:
                if format:
                    json.dump(self.data, f,
                              ensure_ascii=False, indent=4, default=str)
                else:
                    json.dump(self.data, f, default=str)
        except Exception as e:
            logger.error(f'Failed to dump data to file. {self.filepath}, {e}')
            logger.debug(traceback.format_exc())

    def update(self, value, update=True) -> None:
        self.data = value
        update and self.dump()  # type: ignore


class localDict(_localStore):
    def __init__(self, name: str, default: Optional[dict[str, Any]] = None, folder='data') -> None:
        if default is None:
            default = {}
        filepath = folder + '/' + name + '.json'
        super().__init__(filepath, default)
        self.data = cast(dict[str, Any], self.data)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.data:
            del self.data[key]

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def __iter__(self) -> Iterator:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def keys(self) -> KeysView[str]:
        return self.data.keys()

    def values(self) -> ValuesView[Any]:
        return self.data.values()

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def items(self) -> ItemsView[str, Any]:
        return self.data.items()

    def set(self, key: str, value: Any, update=True) -> None:
        self.data[key] = value
        update and self.dump()  # type: ignore

    def delete(self, key: str, update=True) -> None:
        if key in self.data:
            del self.data[key]
        update and self.dump()  # type: ignore

    def clear(self, update=True) -> None:
        self.data.clear()
        update and self.dump()  # type: ignore


class localDictInt(_localStore):
    def __init__(self, name: str, default: Optional[dict[int, Any]] = None, folder='data') -> None:
        if default is None:
            default = {}
        filepath = folder + '/' + name + '.json'
        super().__init__(filepath, default)
        self.data = {int(k): v for k, v in self.data.items()}

    def __getitem__(self, key: int) -> Any:
        return self.data[key]

    def __setitem__(self, key: int, value: Any) -> None:
        self.data[key] = value

    def __delitem__(self, key: int) -> None:
        if key in self.data:
            del self.data[key]

    def __contains__(self, key: int) -> bool:
        return key in self.data

    def __iter__(self) -> Iterator:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def keys(self) -> KeysView[int]:
        return self.data.keys()

    def values(self) -> ValuesView[Any]:
        return self.data.values()

    def get(self, key: int) -> Any:
        return self.data.get(key)

    def items(self) -> ItemsView[int, Any]:
        return self.data.items()

    def set(self, key: int, value: Any, update=True) -> None:
        self.data[key] = value
        if update:
            self.dump()

    def delete(self, key: int, update=True) -> None:
        if key in self.data:
            del self.data[key]
        if update:
            self.dump()

    def clear(self, update=True) -> None:
        self.data.clear()
        update and self.dump()  # type: ignore


class localList(_localStore):
    def __init__(self, name: str, default: Optional[list[Any]] = None, folder: str = 'data') -> None:
        if default is None:
            default = []
        filepath = folder + '/' + name + '.json'
        super().__init__(filepath, default)
        self.data = cast(list[Any], self.data)

    def __getitem__(self, index: int | slice) -> Any:
        return self.data[index]

    def __setitem__(self, index: int, item: Any) -> None:
        self.data[index] = item

    def __delitem__(self, index: int | slice) -> None:
        del self.data[index]

    def __contains__(self, item: Any) -> bool:
        return item in self.data

    def __iter__(self) -> Iterator:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def set(self, index: int, item: Any, update=True) -> None:
        self.data[index] = item
        if update:
            self.dump()

    def append(self, item: Any, update=True) -> None:
        self.data.append(item)
        if update:
            self.dump()

    def remove(self, item: Any, update=True) -> None:
        self.data.remove(item)
        if update:
            self.dump()

    def clear(self, update=True) -> None:
        self.data.clear()
        update and self.dump()  # type: ignore


class localStr(_localStore):
    def __init__(self, name: str, default: Optional[str] = None, folder: str = 'data') -> None:
        if default is None:
            default = ''
        filepath = folder + '/' + name + '.json'
        super().__init__(filepath, default)
        self.data = cast(str, self.data)

    def __iter__(self) -> Iterator:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)


class localInt(_localStore):
    def __init__(self, name: str, default: int = 0, folder: str = 'data') -> None:
        filepath = folder + '/' + name + '.json'
        super().__init__(filepath, default)
        self.data = int(self.data)


class localCookies:
    """
    Local cookies.
    """

    def __init__(self, name, fields) -> None:
        """
        :param name: file name
        :param fields: fields to be stored
        """
        self.valid = True
        self.fields = fields
        self.data = localDict(name, {x: '' for x in fields}, folder='secret')

    def get(self) -> str:
        """
        Get cookies.
        """
        return '; '.join(f'{k}={v}' for k, v in self.data.items())

    def update(self, content):
        """
        Update cookies.
        """
        for field in self.fields:
            r = re.search(f'{field}=([^;]+)', content)
            if r is not None:
                self.data[field] = r.group(1)
        self.data.dump()
        self.valid = True

    def expired(self):
        """
        Check if the cookies is expired.
        """
        self.valid = False
