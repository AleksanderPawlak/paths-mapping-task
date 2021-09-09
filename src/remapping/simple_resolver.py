import typing

from .utils import get_path_resolver, System, normalize_path


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
        # TODO: write that it does not resolve symilnks if given path is on local machine.
        # TODO: write that if platform param is invalid function
        # could possibly incorrectly remap paths
        # TODO: If PurePath won't be removed note why.
        # (Assuming System might lead to incorrect handling of paths).
        # Maybe note that it doesn't handle relative paths
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
            source_sub_path, dst_path = next(
                (
                    (source_sub_path, dst_path)
                    for source_sub_path, dst_path in self.mapping.items()
                    if path_resolver(source_sub_path)
                    in path_resolver(input_path).parents
                ),
                (None, None),
            )
            if not source_sub_path or not dst_path:
                result.append(input_path)
                continue

            dst_path = path_resolver(dst_path)
            sub_path = input_path[len(source_sub_path) :]  # FIXME: Code duplications
            sub_path = sub_path.strip("/").strip("\\")
            result_path = dst_path.joinpath(sub_path)
            result.append(str(result_path))

        return result
