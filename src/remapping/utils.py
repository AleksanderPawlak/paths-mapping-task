import pathlib
import re

WINDOWS_PARENT_PATH_PATTERN = re.compile(r"(/|\\).[^\.\./\\]*(/|\\)\.\.")
POSIX_PARENT_PATH_PATTERN = re.compile(r"(/).[^\.\./]*(/)\.\.")
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

    parent_path_pattern = (
        WINDOWS_PARENT_PATH_PATTERN
        if WINDOWS_PATH_INDICATOR.search(path)
        else POSIX_PARENT_PATH_PATTERN
    )

    # This could be done by pathlib.Path.resolve method but it would be impossible
    # to handle paths from different platforms than host.
    while parent_path_pattern.search(path):
        path = parent_path_pattern.sub("", path)

    path = MULTIPLE_BACKSLASHES_PATTERN.sub(
        r"\\", MULTIPLE_SLASHES_PATTERN.sub("/", path)
    )

    return path


def get_resolved_path(path: str) -> pathlib.PurePath:
    """
    Returns PurePath (PureWindowsPath or PurePosixPath) representation of input path.
    Path style is recognised based on beginning format. Relative paths are not supported.

    Args:
    path (str): path to resolve.

    Returns:
        pathlib.PurePath: instance of PurePath representing input path.

    """
    resolver = (
        pathlib.PureWindowsPath
        if WINDOWS_PATH_INDICATOR.search(path)
        else pathlib.PurePosixPath
    )
    return resolver(normalize_path(path))


def build_dst_path(input_path: str, part_to_replace: str, replacement_path: str) -> str:
    """
    Replaces beginning part of input path with given replacement.
    Please note that all values should be valid, normalized paths.
    Examples:
        >>> build_dst_path("L:\temp", "L:\", "G:\")
        "G:\temp"

    Args:
    input_path (str): path in which given part should be replaced.
    part_to_replace (str): beginning part of path to replace.
    replacement_path (str): replacement.

    Returns:
        str: resolved path

    """
    sub_path = input_path[len(part_to_replace) :]
    sub_path = sub_path.lstrip("/")
    if WINDOWS_PATH_INDICATOR.search(input_path):
        sub_path = sub_path.lstrip("\\")

    replacement_path = get_resolved_path(replacement_path)
    return str(replacement_path.joinpath(sub_path))
