from rest_framework import exceptions, status
from rest_framework.response import Response


class HandleException:
    """
    Mixin to handle exceptions and return a consistent response structure for different error types.
    """

    def handle_exception(self, exc):
        """
        Handles various exceptions and returns an appropriate response.

        Returns:
            Response: A DRF Response object with a standardized error message and HTTP status code.
        """
        if isinstance(exc, exceptions.AuthenticationFailed):
            return Response(
                {
                    "status": False,
                    "message": exc.default_detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if isinstance(exc, exceptions.NotAuthenticated):
            return Response(
                {
                    "status": False,
                    "message": exc.detail,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if isinstance(exc, exceptions.PermissionDenied):
            return Response(
                {
                    "status": False,
                    "message": exc.detail,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        if isinstance(exc, exceptions.ValidationError):
            try:
                message = exc.detail[next(iter(exc.detail))][0]
            except:
                message = exc.detail
            return Response(
                {
                    "status": False,
                    "message": message,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if isinstance(exc, Exception):
            return Response(
                {
                    "status": False,
                    "message": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().handle_exception(exc)
