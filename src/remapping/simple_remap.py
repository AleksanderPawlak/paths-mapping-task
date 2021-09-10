import typing

from .utils import get_resolved_path, normalize_path, build_dst_path


class SimpleRemap:
    # If we want to handle relative paths etc. target platform should be passed to __call__
    # Something like on "platform-passed-by-user" branch.
    """Class for remapping paths with the same source, destination platform and path style.

    The purpose of this class is to remap list of given paths to paths in the same style
    listed in mapping.
    It does not support relative paths on host machine, so only absolute paths are supported.
    Paths style and platform is recognised based on beginning of absolute path.
    Windows style paths begins with "DISC_LETTER:\".
    POSIX (Linux/Mac/...) paths should begin with "/...", paths in form "~/dir" are not supported.
    Parent statements in input and mapping paths are be resolved, e.g. "/mnt/../mnt2" -> "/mnt2".
    It does support windows style multiplications of folders separator like "G:\\\\\\dir"

    Examples:
        >>> remap = SimpleRemap({"L:\": "X:\"})
        >>> remap(["L:\temp"])
        ["X:\temp"]

    Attributes:
        mapping (typing.Dict[str, str]): Paths mapping. More information in __init__ doc.
    """

    def __init__(self, mapping: typing.Dict[str, str]):
        """
        Args:
            mapping (typing.Dict[str, str]): Paths mapping.
                Each key and value should represent sub path and it's replacement respectively,
                i.e. { desired-sub-path-to-replace: replacement, ... }
        """
        self.mapping = mapping

    def __call__(self, input_paths: typing.List[str]) -> typing.List[str]:
        """
        Args:
            input_paths (typing.List[str]): Input paths to remap.

        Returns:
            typing.List[str]: List of remapped input paths

        """
        result = []

        for input_path in input_paths:
            input_path = normalize_path(input_path)
            matching_parent_path, dst_path = next(
                filter(
                    lambda v: get_resolved_path(v[0])
                    in get_resolved_path(input_path).parents,
                    self.mapping.items(),
                ),
                (None, None),
            )
            if not matching_parent_path or not dst_path:
                result.append(input_path)
                continue

            dst_path = normalize_path(dst_path)
            result.append(build_dst_path(input_path, matching_parent_path, dst_path))

        return result
