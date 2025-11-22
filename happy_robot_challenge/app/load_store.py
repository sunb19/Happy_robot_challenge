# app/load_store.py
import json
from pathlib import Path
from typing import List

from .schemas import Load, LoadSearchQuery

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "loads.json"


class LoadStore:
    def __init__(self, data_path: Path = DATA_PATH) -> None:
        self.data_path = data_path
        self._loads: List[Load] = []
        self._load_data()

    def _load_data(self) -> None:
        if not self.data_path.exists():
            self._loads = []
            return
        with self.data_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        self._loads = [Load(**item) for item in raw]

    def list_all(self) -> List[Load]:
        return self._loads

    def search(self, query: LoadSearchQuery) -> List[Load]:
        def matches(load: Load) -> bool:
            if query.origin and query.origin.lower() not in load.origin.lower():
                return False
            if query.destination and query.destination.lower() not in load.destination.lower():
                return False
            if query.equipment_type and query.equipment_type.lower() != load.equipment_type.lower():
                return False
            return True

        return [l for l in self._loads if matches(l)]

    def get_by_id(self, load_id: str) -> Load:
        for l in self._loads:
            if l.load_id == load_id:
                return l
        raise KeyError(f"Load with id {load_id} not found")


load_store = LoadStore()
