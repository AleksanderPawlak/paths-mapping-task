import enum
import pathlib
import re
import typing

PARENT_PATH_PATTERN = re.compile(r"(/|\\).[^\.\./\\]*(/|\\)\.\.")
MULTIPLE_BACKSLASHES_PATTERN = re.compile(r"\\+")
MULTIPLE_SLASHES_PATTERN = re.compile(r"/+")


class System(enum.Enum):
    WINDOWS = enum.auto()
    LINUX = enum.auto()
    MAC = enum.auto()


POSIX_PLATFORMS: typing.Final[typing.Iterable[System]] = (System.LINUX, System.MAC)


# This method was defined to resolve parent path symbols regardless of host system
# (thus not os or pathlib).
def normalize_path(path: str) -> str:
    """
    Resolves parent path symbols in path (e.g. "/mnt/../some_path") and
    normalizes multiplied slashes and backslashes (e.g. G:\\\\\\some_dir)
    Please not that relative paths like "../some_pah/" won't be resolved.

    Args:
    path (str): input path, in which parent paths should be normalized.

    Returns:
        str: resolved path

    """
    while PARENT_PATH_PATTERN.search(path):
        path = PARENT_PATH_PATTERN.sub("", path)

    path = MULTIPLE_BACKSLASHES_PATTERN.sub(
        r"\\", MULTIPLE_SLASHES_PATTERN.sub("/", path)
    )

    return path


def get_path_resolver(platform: System) -> typing.Type[pathlib.PurePath]:
    """
    Args:
    platform (System): Given system.

    Returns:
        typing.Type[pathlib.PurePath]: subtype of PurePath specific to given platform.

    """
    path_resolver = {
        System.WINDOWS: pathlib.PureWindowsPath,
        System.LINUX: pathlib.PurePosixPath,
        System.MAC: pathlib.PurePosixPath,
    }.get(platform)
    if path_resolver is None:
        raise ValueError(f"Passed platform: '{platform}' is not supported.")

    return path_resolver


def build_dst_path(
    input_path: str, part_to_replace: str, replacement_path: pathlib.PurePath
) -> str:
    sub_path = input_path[len(part_to_replace) :]
    sub_path = sub_path.strip("/").strip("\\")
    return str(replacement_path.joinpath(sub_path))
