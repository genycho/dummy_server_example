class DummyServerException(Exception):
    def __init__(self, message):
        self.value = message

    def __str__(self):
        return self.value
