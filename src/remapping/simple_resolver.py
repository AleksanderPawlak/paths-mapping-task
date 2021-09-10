import typing

from .utils import get_path_resolver, System, normalize_path, build_dst_path


class SimpleRemap:
    def __init__(self, mapping: typing.Dict[str, str]):
        """
        Args:
            mapping (typing.Dict[str, str]): Paths mapping.
                Each key and value should represent sub path and it's replacement respectively,
                i.e. { desired-sub-path-to-replace: replacement, ... }
        """
        self.mapping = mapping

    def __call__(
        self, input_paths: typing.List[str], platform: System
    ) -> typing.List[str]:
        """
        Args:
            input_paths (typing.List[str]): Input paths to remap.
            platform (System): System corresponding to input paths.

        Returns:
            typing.List[str]: List of remapped input paths

        """
        path_resolver = get_path_resolver(platform)
        result = []

        for input_path in input_paths:
            input_path = normalize_path(input_path)
            matching_parent_path, dst_path = next(
                filter(
                    lambda v: path_resolver(v[0]) in path_resolver(input_path).parents,
                    self.mapping.items(),
                ),
                (None, None),
            )
            if not matching_parent_path or not dst_path:
                result.append(input_path)
                continue

            dst_path = path_resolver(normalize_path(dst_path))
            result.append(build_dst_path(input_path, matching_parent_path, dst_path))

        return result
