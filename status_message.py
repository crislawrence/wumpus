class StatusMessage:
    """
    Mechanism for holding the details of the game state.  Note that even construction of a single status message
    is incorporated into a list so that I could use 'extend' always rather than have to determine when 'append' was
    more applicable.  I did this because the list of status messages grows, method by method.
    """

    def __init__(self, type, source, content):
        """
        Message describing some aspect of the game state.  The type and souce of the message were used for filtering
        and highlighting.
        :param type: INFO, WARNING, TERMINAL
        :param source: WUMPUS, BOTTOMLESS_PIT, BAT_COLONY, GENERAL
        :param content: message content.
        """
        self.type = type
        self.source = source
        self.content = content

    def __str__(self):
        return f"Status message: type: {self.type}, source: {self.source}, content: {self.content}"

    def __repr__(self):
        return f"Status message: type: {self.type}, source: {self.source}, content: {self.content}"

    def to_json(self):
        """
        Converts the object into a json compatible dictionary that can be delivered via ajax.
        :return: json compatible dictionary
        """
        return {
            "type": self.type,
            "source": self.source,
            "content": self.content
        }