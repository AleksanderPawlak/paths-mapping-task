import enum
import pathlib
import re
import typing

PARENT_PATH_PATTERN = re.compile(r"(/|\\).[^\.\./\\]*(/|\\)\.\.")
MULTIPLE_BACKSLASHES_PATTERN = re.compile(r"\\+")
MULTIPLE_SLASHES_PATTERN = re.compile(r"/+")
WINDOWS_PATH_INDICATOR = re.compile(r"[\w]\:")


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


def get_resolved_path(path: str) -> pathlib.PurePath:
    """
    Args:
    path (str): path to resolve.

    Returns:
        pathlib.PurePath: instance of PurePath representing input path.

    """
    resolver = (
        pathlib.PureWindowsPath
        if WINDOWS_PATH_INDICATOR.match(path)
        else pathlib.PurePosixPath
    )
    return resolver(path)


def build_dst_path(input_path: str, part_to_replace: str, replacement_path: str) -> str:
    sub_path = input_path[len(part_to_replace) :]
    sub_path = sub_path.strip("/").strip("\\")
    replacement_path = get_resolved_path(replacement_path)
    return str(replacement_path.joinpath(sub_path))
