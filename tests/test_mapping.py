import unittest

from src import remapping


class TestMapping(unittest.TestCase):
    def test_remap_paths_from_the_same_platform(self):
        # TODO: think about other input data format
        input_mapping = {
            "L:\\": "X:\\",
            "P:\\project1\\textures": "Z:\\library\\textures",
        }
        input_paths = [
            "L:\\temp",
            "p:/project1/textures\\grass.tga",
            "P:\\project1\\assets\\env\\Forest",
            "cache\\Tree.abc",
            "g:\\nope",
        ]
        expected_result = [
            "X:\\temp",
            "Z:\\library\\textures\\grass.tga",
            "P:\\project1\\assets\\env\\Forest",
            "cache\\Tree.abc",
            "g:\\nope",
        ]
        result = remapping.tools.remap(
            input_mapping, input_paths, remapping.tools.System.WINDOWS
        )

        self.assertEqual(expected_result, result)

    # def test_remap_paths_from_different_platforms(self):
    #     ...

    # def test_remap_from_mixed_platforms(self):
    #     ...

    # TODO: test other failing cases
    # def test_remap_mixed_platforms_with_different_paths_number_should_raise_error(self):
    #     ...
