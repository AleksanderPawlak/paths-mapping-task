import typing
import enum
import pathlib


# TODO: is there a way to differentiate between systems without passing the system?
class System(enum.Enum):
    WINDOWS = enum.auto()
    POSIX = enum.auto()


def remap(
    mapping: typing.Dict[str, str], input_paths: typing.List[str], platform: System
) -> typing.List[str]:
    # TODO: maybe without PurePathLib?
    path_resolver = {
        System.WINDOWS: pathlib.PureWindowsPath,
        System.POSIX: pathlib.PurePosixPath,
    }.get(platform)
    if path_resolver is None:
        raise ValueError(f"Passed platform: {platform} is not supported.")

    result = []

    # FIXME: This loop could be probably better.
    for input_path in input_paths:
        for key, value in mapping.items():
            if path_resolver(key) in path_resolver(input_path).parents:
                result_path = value + input_path[len(key) :]
                result.append(result_path)
                break
        else:
            result.append(input_path)

    return result
