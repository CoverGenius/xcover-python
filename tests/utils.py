class MockResponse:
    def __init__(self, status_code: int, data: dict = None):
        self.status_code = status_code
        self.data = data or {}

    def json(self):
        return self.data
