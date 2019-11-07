class StatusMessage:

    def __init__(self, type, source, content):
        self.type = type
        self.source = source
        self.content = content

    def __str__(self):
        return f"Status message: type: {self.type}, source: {self.source}, content: {self.content}"

    def __repr__(self):
        return f"Status message: type: {self.type}, source: {self.source}, content: {self.content}"

    def to_json(self):
        return {
            "type": self.type,
            "source": self.source,
            "content": self.content
        }