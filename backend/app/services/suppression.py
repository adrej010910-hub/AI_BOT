from dataclasses import dataclass

@dataclass
class SuppressionList:
    emails: set[str]

    def contains(self, email: str | None) -> bool:
        return bool(email) and email.lower().strip() in self.emails

    def add(self, email: str) -> None:
        self.emails.add(email.lower().strip())

SUPPRESSION = SuppressionList(set())
