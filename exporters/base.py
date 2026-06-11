from abc import ABC, abstractmethod


class BaseExporter(ABC):
    @abstractmethod
    def export(self, databag: dict, output_path: str) -> str:
        pass
