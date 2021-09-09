import typing
import enum
import pathlib


# TODO: is there a way to differentiate between systems without passing the system value?
class System(enum.Enum):
    WINDOWS = enum.auto()
    LINUX = enum.auto()
    MAC = enum.auto()


POSIX_PLATFORMS: typing.Final[typing.Iterable[System]] = (System.LINUX, System.MAC)


def get_path_resolver(platform: System) -> typing.Type[pathlib.PurePath]:
    # TODO: maybe without PurePathLib?
    path_resolver = {
        System.WINDOWS: pathlib.PureWindowsPath,
        System.LINUX: pathlib.PurePosixPath,
        System.MAC: pathlib.PurePosixPath,
    }.get(platform)
    if path_resolver is None:
        raise ValueError(f"Passed platform: '{platform}' is not supported.")

    return path_resolver


# TODO: maybe these two classes should be merged?


class SimpleRemap:
    def __init__(self, mapping: typing.Dict[str, str]):
        self.mapping = mapping

    def __call__(
        self, input_paths: typing.List[str], platform: System
    ) -> typing.List[str]:
        path_resolver = get_path_resolver(platform)
        result = []

        for input_path in input_paths:
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
            sub_path = input_path[len(source_sub_path) :].strip("/").strip("\\")
            result_path = dst_path.joinpath(sub_path)
            result.append(str(result_path))

        return result


class MixedPlatformRemap:
    def __init__(self, mapping: typing.Dict[System, typing.List[typing.Optional[str]]]):
        if len(set(len(paths) for platform, paths in mapping.items())) != 1:
            raise ValueError(
                f"Paths lists in mapping should have the same size. Given mapping: {mapping}"
            )

        self.mapping = mapping

    def __call__(
        self, input_paths: typing.List[str], dst_platform: System
    ) -> typing.List[str]:
        if dst_platform not in self.mapping:
            raise ValueError(
                f"Destination platform '{dst_platform}'"
                f" was not specified in input mapping: {self.mapping}"
            )

        dst_platform_is_posix = dst_platform in POSIX_PLATFORMS
        dst_paths = self.mapping[dst_platform]
        dst_resolver = get_path_resolver(dst_platform)
        result = []
        # FIXME: ugly nested loops and breaks
        for input_path in input_paths:
            for platform, paths in self.mapping.items():
                if platform == dst_platform:
                    continue

                path_resolver = get_path_resolver(platform)
                for idx, path in enumerate(paths):
                    if not path or not dst_paths[idx]:
                        continue

                    resolved_input_path = path_resolver(input_path)
                    if path_resolver(path) in resolved_input_path.parents:
                        resolved_input_path = (
                            resolved_input_path.as_posix()
                            if dst_platform_is_posix
                            else str(resolved_input_path)
                        )
                        sub_path = (
                            resolved_input_path[len(path) :].strip("/").strip("\\")
                        )
                        result_path = dst_resolver(dst_paths[idx]).joinpath(sub_path)
                        result.append(str(result_path))
                        break
                else:
                    continue
                break
            else:
                result.append(input_path)

        return result
