class NotFoundError(Exception):
    def __init__(self, message="Not found 404"):
        self.message = message
        super().__init__(self.message)


class BadRequestError(Exception):
    def __init__(self, message="Bad Request 400"):
        self.message = message
        super().__init__(self.message)


class BadRequestInModalError(Exception):
    def __init__(self, message="Bad Request in modal 400"):
        self.message = message
        super().__init__(self.message)
