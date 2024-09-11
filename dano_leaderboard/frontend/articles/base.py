from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

@dataclass
class BaseArticle(ABC):
    title: str
    date: datetime
    teaser: str

    @abstractmethod
    def content(self):
        ...
