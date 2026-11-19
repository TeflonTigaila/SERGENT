import errno
import hashlib
import json
import os
import shutil
import sys
import tempfile
from collections.abc import Callable
from datetime import date, time
from pathlib import Path

from cust_errors import *

def _fsync_dir(dir:Path) ->None:
    d=os.open(dir , os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(d)
    finally:
        os.close(d)

def save_atomic(path: Path, data: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        _fsync_dir(path.parent)
    except BaseException:
        os.unlink(tmp)
        raise

def anal(string: str) -> bool:
    try:
        d = list(map(int, string.split("-")))
        if not 1<=len(d)<=3:
            return False
        day, mon, yea = (d + [1, 2000][len(d) - 1:])[:3]
        date(yea ,mon ,day)
        return True
    except (TypeError , ValueError):
        return False


def is_time(string: str) -> bool:
    try:
        d = list(map(int, string.split(":")))
        d.extend([0] * (3 - len(d)))
        ore,min,sec = d
        time(ore,min,sec)
        return True
    except (TypeError,ValueError):
        return False


def data_enum(text: str, anal: Callable) -> list[str]:
    items: list[str] = []
    try:
        i: int = 0
        print(text)
        while True:
            try:
                items.append(input(f"[{i}]>>"))
                if anal(items[i]):
                    i = i + 1
                else:
                    raise ValueError
            except ValueError:
                print(f"Inaccepted form of data {items[i]}")
                items.pop()
                continue
    except EOFError:
        print(items)
    return items


def event_data() -> dict[str, list[str]]:
    return {
        "date": data_enum("DATE FORMAT IS (DD-MM-YYYY DD-MM DD )", anal),
        "time": data_enum("TIME FORMAT IS (HH:MM:SS HH:MM HH )", is_time),
        "command": data_enum(
            "INSERT THE COMANDS IN THE ORDER YOU WANT THEM TU RUN", lambda x: True
        ),
    }


class DB_API:
    def __init__(self, data: dict[str, dict[str, list[str]]], db_path:Path) -> None:
        self.db_path:Path = db_path
        self.db_bk_path:Path = db_path.with_suffix(".bak")
        self.data = data

    def GET(self):
        return self.data

    def POST(self, event_name: str):
        self.data[event_name] = event_data()
        save_atomic(self.db_path, self.data)

    def DEL(self, event_name: str):
        del self.data[event_name]
        save_atomic(self.db_path, self.data)

def DB_extractor(file: Path) -> dict[str, dict[str, list[str]]]:
    try:
        return json.loads(file.read_text())
    except FileNotFoundError:
        raise invalid_date_argument


def main(event_list: str) -> None:
    if event_list is None:
        raise missing_date_argument()
    DB_file: Path = Path(event_list).expanduser().resolve()
    DB_content: dict[str, dict[str, list[str]]] = DB_extractor(DB_file)
    DB_api: DB_API = DB_API(DB_content , DB_file)


if __name__ == "__main__":
    main(sys.argv[1])
