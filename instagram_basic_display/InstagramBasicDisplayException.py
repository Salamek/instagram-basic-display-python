
class InstagramBasicDisplayException(Exception):
    def __init__(self, message: str, error_type: str = None, error_code: int = None, error_fbtrace_id: str = None):
        super().__init__(message)

        self.error_type = error_type
        self.error_code = error_code
        self.error_fbtrace_id = error_fbtrace_id

    @staticmethod
    def from_error_response(error: dict):
        return InstagramBasicDisplayException(
            error.get('message'),
            error.get('type'),
            error.get('code'),
            error.get('fbtrace_id')
        )

    def __str__(self):
        return '{}: Type: {}, Code: {}, FBTraceID: {}'.format(
            super().__str__(),
            self.error_type,
            self.error_code,
            self.error_fbtrace_id
        )