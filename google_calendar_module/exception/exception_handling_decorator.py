import domain.slack.slack_utils as util
from exception.errors import NotFoundError, BadRequestError
from schemas import HttpErrorResponse


class HttpExceptionHanlder:
    def http_error_handle(self, func):
        def wrapper(*args):
            try:
                response = func(args)
                return response
            except BadRequestError as e:
                response = {"message": e.args[0], "status_code": 400}
                return HttpErrorResponse(**response)
            except NotFoundError as e:
                response = {"message": e.args[0], "status_code": 404}
                return HttpErrorResponse(**response)
            finally:
                util.debug_message_for_decorator(f"response: {response}")

        return wrapper


handler = HttpExceptionHanlder()
