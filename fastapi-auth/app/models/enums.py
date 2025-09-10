import enum

class UserRole(str, enum.Enum):
    trainer = "trainer"
    client = "client"
