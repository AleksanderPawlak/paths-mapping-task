import typing

from .utils import (
    System,
    POSIX_PLATFORMS,
    normalize_path,
    get_path_resolver,
    build_dst_path,
)


class MixedPlatformRemap:
    def __init__(self, mapping: typing.Dict[System, typing.List[typing.Optional[str]]]):
        """
        Args:
            mapping (typing.Dict[System, typing.List[typing.Optional[str]]]): Paths mapping.
                Each key and value should represent System and list of paths respectively,
                i.e. { paths-system: [path, ...], ... }.
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
        self, input_paths: typing.List[str], dst_platform: System
    ) -> typing.List[str]:
        """
        Args:
            input_paths (typing.List[str]): Input paths to remap.
            dst_platform (System): Destination system from mapping,
                to which all input paths whose parents are listed in mapping should be mapped.

        Returns:
            typing.List[str]: List of remapped input paths

        """
        if dst_platform not in self.mapping:
            raise ValueError(
                f"Destination platform '{dst_platform}'"
                f" was not specified in input mapping: {self.mapping}"
            )

        dst_platform_is_posix = dst_platform in POSIX_PLATFORMS
        dst_paths = self.mapping[dst_platform]
        dst_resolver = get_path_resolver(dst_platform)
        result = []

        for input_path in input_paths:
            input_path = normalize_path(input_path)
            for platform, platform_paths in self.mapping.items():
                if platform == dst_platform:
                    continue

                path_resolver = get_path_resolver(platform)
                resolved_input_path = path_resolver(input_path)
                replacement_id, matching_parent_path = next(
                    filter(
                        lambda x: x[1]
                        and dst_paths[x[0]]
                        and path_resolver(x[1]) in resolved_input_path.parents,
                        enumerate(platform_paths),
                    ),
                    (None, None),
                )

                if replacement_id is None or not matching_parent_path:
                    continue

                resolved_input_path = (
                    resolved_input_path.as_posix()
                    if dst_platform_is_posix
                    else str(resolved_input_path)
                )
                dst_path = dst_resolver(normalize_path(dst_paths[replacement_id]))
                result.append(
                    build_dst_path(resolved_input_path, matching_parent_path, dst_path)
                )
                break

            else:
                result.append(input_path)

        return result
