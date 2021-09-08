import typing
import enum
import pathlib


# TODO: is there a way to differentiate between systems without passing the system?
class System(enum.Enum):
    WINDOWS = enum.auto()
    POSIX = enum.auto()
    # TODO: LINUX and Mac instead of POSIX


def get_path_resolver(platform: System) -> typing.Type[pathlib.PurePath]:
    # TODO: maybe without PurePathLib?
    # Can PureWindowsPath deal with all kinds of paths? What about relative paths
    path_resolver = {
        System.WINDOWS: pathlib.PureWindowsPath,
        System.POSIX: pathlib.PurePosixPath,
    }.get(platform)
    if path_resolver is None:
        raise ValueError(f"Passed platform: {platform} is not supported.")

    return path_resolver


def remap(
    mapping: typing.Dict[str, str], input_paths: typing.List[str], platform: System
) -> typing.List[str]:
    path_resolver = get_path_resolver(platform)
    result = []

    # FIXME: This loop could be probably better.
    for input_path in input_paths:
        # FIXME: key, value <- rename
        for key, value in mapping.items():
            if path_resolver(key) in path_resolver(input_path).parents:
                result_path = value + input_path[len(key) :]
                result.append(result_path)
                break
        else:
            result.append(input_path)

    return result


# TODO: maybe these two functions should be merged?
def remap_cross_platform(
    mapping: typing.Dict[System, typing.Iterable[str]],
    input_paths: typing.List[str],
    dst_platform: System,
) -> typing.List[str]:
    dst_paths = mapping.pop(dst_platform)
    dst_resolver = get_path_resolver(dst_platform)
    result = []
    # FIXME: ugly nested loops and breaks
    for input_path in input_paths:
        for platform, paths in mapping.items():
            path_resolver = get_path_resolver(platform)
            for idx, path in enumerate(paths):
                resolved_input_path = path_resolver(input_path)
                if path_resolver(path) in resolved_input_path.parents:
                    resolved_input_path = (
                        resolved_input_path.as_posix()
                        if dst_platform == System.POSIX
                        else str(resolved_input_path)
                    )
                    result_path = dst_resolver(dst_paths[idx]).joinpath(
                        resolved_input_path[len(path) :]
                    )
                    result.append(str(result_path))
                    break
            else:
                continue
            break
        else:
            result.append(input_path)

    return result
