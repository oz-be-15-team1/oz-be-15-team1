from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings


class OptionalBearerJWTAuthentication(JWTAuthentication):
    def get_raw_token(self, header):
        if header is None:
            return None

        if isinstance(header, (bytes, bytearray)):
            header = header.decode("utf-8")

        parts = header.split()
        header_types = api_settings.AUTH_HEADER_TYPES
        if len(parts) == 1:
            return parts[0]
        if len(parts) == 2 and parts[0] in header_types:
            return parts[1]
        return None
