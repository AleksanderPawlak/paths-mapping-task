import typing

from .utils import (
    normalize_path,
    get_resolved_path,
    build_dst_path,
    is_windows_style_path,
)


class MixedPlatformRemap:
    # Remap algorithms were implemented as classes with __call__
    # to handle situations where we want to reuse mapping.
    # With this implementation it's format can be checked once and
    # if some preparation would be needed it would be also done only in init.
    # Overall it will be easier to use reuse it.
    """Class for remapping paths from different platforms and with different styles.

    The purpose of this class is to remap list of given paths to paths
    to destination platform based on paths listed in mapping.

    Just like SimpleRemap it does not support relative paths on host machine,
    so only absolute paths are supported. Paths in form "~/dir" are also not supported.
    Paths style and platform is recognised based on beginning of absolute path.
    Windows style paths begins with "DISC_LETTER:\".
    POSIX (Linux/Mac/...) paths should begin with "/...".
    Parent statements in input and mapping paths are be resolved, e.g. "/mnt/../mnt2" -> "/mnt2".
    It does support windows style multiplications of folders separator like "G:\\\\\\dir"

    Examples:
        >>> remap = MixedPlatformRemap({"Windows": ["L:\"], "Mac": ["/Volumes/storage1"]})
        >>> remap(["L:\temp"], "Mac")
        ["/Volumes/storage1/temp"]

    Attributes:
        mapping (typing.Dict[str, typing.List[typing.Optional[str]]]): Paths mapping.
            More information in __init__ doc.
    """

    def __init__(self, mapping: typing.Dict[str, typing.List[typing.Optional[str]]]):
        """
        Args:
            mapping (typing.Dict[str, typing.List[typing.Optional[str]]]): Paths mapping.
                Each key and value should represent platform and list of paths respectively,
                i.e. { paths-platform: [path, ...], ... }.
                Each path presented in mapping correspond to paths at
                the same index in paths listed for different systems.
        """
        if any(
            paths for paths in mapping.values() if not isinstance(paths, (list, tuple))
        ):  # This could be also done with external lib like typeguard
            raise ValueError(
                f"Incorrect format of input mapping: '{mapping}'. "
                f"Should be dict of str keys and list or tuple values."
            )

        if len(set(len(paths) for paths in mapping.values())) != 1:
            raise ValueError(
                f"Paths lists in mapping should have the same size. Given mapping: {mapping}"
            )

        self.mapping = mapping

    def __call__(
        self, input_paths: typing.List[str], dst_platform: str
    ) -> typing.List[str]:
        """
        Args:
            input_paths (typing.List[str]): Input paths to remap.
            dst_platform (str): Destination platform from mapping,
                to which all input paths whose parents are listed in mapping should be mapped.

        Returns:
            typing.List[str]: List of remapped input paths

        """
        if dst_platform not in self.mapping:
            raise ValueError(
                f"Destination platform '{dst_platform}'"
                f" was not specified in input mapping: {self.mapping}"
            )

        dst_paths = self.mapping[dst_platform]
        result = []

        for input_path in input_paths:
            for platform, platform_paths in self.mapping.items():
                if platform == dst_platform:
                    continue

                resolved_input_path = get_resolved_path(input_path)
                replacement_id, matching_parent_path = next(
                    filter(
                        lambda v: (dst_paths[v[0]] and v[1])
                        and get_resolved_path(v[1]) in resolved_input_path.parents,
                        enumerate(platform_paths),
                    ),
                    (None, None),
                )

                if replacement_id is None or not matching_parent_path:
                    continue

                dst_path = normalize_path(dst_paths[replacement_id])
                if not is_windows_style_path(dst_path):
                    resolved_input_path = resolved_input_path.as_posix()

                result.append(
                    build_dst_path(
                        str(resolved_input_path), matching_parent_path, dst_path
                    )
                )
                break

            else:
                result.append(input_path)

        return result
