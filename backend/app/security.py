from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    CATALOGER = "cataloger"
    VIEWER = "viewer"