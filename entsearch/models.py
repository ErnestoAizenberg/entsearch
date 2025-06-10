from typing import Any, Optional

__all__ = ["Dataset", "Entity", "User", "nlp_model"]


# Domain models
class User:
    _id_counter: int = 0

    def __init__(
        self, email: str, username: str, password: str, created: Optional[str] = None
    ) -> None:
        self.id: int = self._generate_id()
        self.created: Optional[str] = created
        self.email: str = email
        self.username: str = username
        self.password: str = password

    def _generate_id(self) -> int:
        self._id_counter += 1
        return self._id_counter

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, email='{self.email}', username='{self.username}', "
            f"created='{self.created}')"
        )


class Dataset:
    _id_counter: int = 0

    def __init__(self, title: str, password: str, user_id: int, created: str) -> None:
        self.id: int = self._generate_id()
        self.title: str = title
        self.password: str = password
        self.user_id: int = user_id
        self.created: str = created

    def _generate_id(self) -> int:
        self._id_counter += 1
        return self._id_counter

    def __repr__(self) -> str:
        return (
            f"Dataset(id={self.id}, title='{self.title}', user_id={self.user_id}, "
            f"created='{self.created}')"
        )


class Entity:
    _id_counter: int = 0

    def __init__(
        self,
        dataset_id: int,
        entity_name: str,
        entity_name_embed: Any,
        description: str,
        foreign_identifier: str,
    ) -> None:
        self.id: int = self._generate_id()
        self.dataset_id: int = dataset_id
        self.entity_name: str = entity_name
        self.entity_name_embed: Any = entity_name_embed
        self.description: str = description
        self.foreign_identifier: str = foreign_identifier

    def _generate_id(self) -> int:
        self._id_counter += 1
        return self._id_counter

    def __repr__(self) -> str:
        return (
            f"Entity(id={self.id}, dataset_id={self.dataset_id}, "
            f"entity_name='{self.entity_name}', description='{self.description}', "
            f"foreign_identifier='{self.foreign_identifier}')"
        )


def nlp_model(text):
    return [0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [1, 2, 3, 4, 5, 98]
