from dataclasses import dataclass


@dataclass
class Mention:
	prefix: str
	mentioned_id: int

	def __str__(self) -> str:
		return f"<{self.prefix}{self.mentioned_id}>"