import unittest

from src import remapping


class TestMapping(unittest.TestCase):
    def test_remap_paths_from_different_platforms(self):
        input_mapping = {
            "Windows": ["L:\\", "P:\\"],
            "Mac": ["/Volumes/storage1", "/Volumes/storage2/"],
        }
        input_paths = [
            "L:\\temp",
            "p:/project1/textures\\grass.tga",
            "P:\\\\\\\\\\project1\\assets\\env\\Forest",
            "cache\\Tree.abc",
            "g:\\nope",
        ]
        expected_result = [
            "/Volumes/storage1/temp",
            "/Volumes/storage2/project1/textures/grass.tga",
            "/Volumes/storage2/project1/assets/env/Forest",
            # "cache/Tree.abc",  # This might be a bug in specification. Why should it change?
            "cache\\Tree.abc",
            "g:\\nope",
        ]
        remap = remapping.MixedPlatformRemap(input_mapping)
        result = remap(input_paths, "Mac")

        self.assertEqual(expected_result, result)

    def test_remap_paths_from_different_platforms_with_parent_dir_symbol(self):
        input_mapping = {
            "Windows": ["L:\\", "P:\\"],
            "Linux": ["/mnt/storage1", "/mnt/storage2"],
        }
        input_paths = [
            "/mnt/storage1/project1/assets/prop/Box",
            "/mnt/storage3/project1/textures/wood.tga",
            "/mnt/storage3/../storage1/project1/textures/wood.tga",
            "/mnt/storage3/../../mnt/storage1/project1/textures/tree.tga",
            "/mnt/storage2/project1/textures/wood.tga",
        ]
        expected_result = [
            "L:\\project1\\assets\\prop\\Box",
            "/mnt/storage3/project1/textures/wood.tga",
            "L:\\project1\\textures\\wood.tga",
            "L:\\project1\\textures\\tree.tga",
            "P:\\project1\\textures\\wood.tga",
        ]
        remap = remapping.MixedPlatformRemap(input_mapping)
        result = remap(input_paths, "Windows")

        self.assertEqual(expected_result, result)

    def test_remap_from_mixed_platforms(self):
        input_mapping = {
            "Windows": ["L:\\", "P:\\"],
            "Linux": ["/mnt/storage1", "/mnt/storage2"],
            "Mac": ["/Volumes/storage1", "/Volumes/storage2"],
        }
        input_paths = [
            "L:\\temp",
            "p:/project1/textures\\grass.tga",
            "P:\\project1\\assets\\env\\Forest",
            "cache\\Tree.abc",
            "g:\\nope",
            "/mnt/storage2/project1/assets/prop/Box",
            "/mnt/storage2/project1/textures/wood.tga",
            "/Volumes/storage1/project2/input/20190117",
            "/Volumes/storage1/project2/shots",
        ]
        expected_result = [
            "/mnt/storage1/temp",
            "/mnt/storage2/project1/textures/grass.tga",
            "/mnt/storage2/project1/assets/env/Forest",
            # "cache/Tree.abc",  # This might be a bug in specification.  Why should it change?
            "cache\\Tree.abc",
            "g:\\nope",
            "/mnt/storage2/project1/assets/prop/Box",
            "/mnt/storage2/project1/textures/wood.tga",
            "/mnt/storage1/project2/input/20190117",
            "/mnt/storage1/project2/shots",
        ]
        remap = remapping.MixedPlatformRemap(input_mapping)
        result = remap(input_paths, "Linux")

        self.assertEqual(expected_result, result)

    def test_remap_paths_from_mixed_platforms_with_none_value_in_mappings_source(self):
        input_mapping = {
            "Windows": ["L:\\", "P:\\", "G:\\"],
            "Linux": [
                "/mnt/storage1",
                "/mnt/storage2",
                "/mnt/storage3",
            ],
            "Mac": [
                "/Volumes/storage1",
                None,
                "/Volumes/storage2",
            ],
        }
        input_paths = [
            "L:\\temp",
            "p:/project1/textures\\grass.tga",
            "P:\\project1\\assets\\env\\Forest",
            "cache\\Tree.abc",
            "g:\\yes",
            "/mnt/storage2/project1/assets/prop/Box",
            "/mnt/storage2/project1/textures/wood.tga",
            "/Volumes/storage1/project2/input/20190117",
            "/Volumes/storage2/project2/shots",
        ]
        expected_result = [
            "/mnt/storage1/temp",
            "/mnt/storage2/project1/textures/grass.tga",
            "/mnt/storage2/project1/assets/env/Forest",
            # "cache/Tree.abc",  # This might be a bug in specification
            "cache\\Tree.abc",
            "/mnt/storage3/yes",
            "/mnt/storage2/project1/assets/prop/Box",
            "/mnt/storage2/project1/textures/wood.tga",
            "/mnt/storage1/project2/input/20190117",
            "/mnt/storage3/project2/shots",
        ]
        remap = remapping.MixedPlatformRemap(input_mapping)
        result = remap(input_paths, "Linux")

        self.assertEqual(expected_result, result)

    def test_remap_paths_from_mixed_platforms_with_none_value_in_mappings_dst(self):
        """ "
        If we want to reuse mapping there might be case where there is None value in dst paths.
        """
        input_mapping = {
            "Windows": ["L:\\", "P:\\", "G:\\"],
            "Linux": [
                "/mnt/storage1",
                "/mnt/storage2",
                "/mnt/storage3",
            ],
            "Mac": [
                "/Volumes/storage1",
                None,
                "/Volumes/storage2",
            ],
        }
        input_paths = [
            "L:\\temp",
            "p:/project1/textures\\grass.tga",
            "P:\\project1\\assets\\env\\Forest",
            "cache\\Tree.abc",
            "g:\\yes",
            "/mnt/storage3/project1/assets/prop/Box",
            "/mnt/storage2/project1/textures/wood.tga",
            "/Volumes/storage1/project2/input/20190117",
            "/Volumes/storage2/project2/shots",
        ]
        expected_result = [
            "/Volumes/storage1/temp",
            "p:/project1/textures\\grass.tga",
            "P:\\project1\\assets\\env\\Forest",
            # "cache/Tree.abc",  # This might be a bug in specification.
            "cache\\Tree.abc",
            "/Volumes/storage2/yes",
            "/Volumes/storage2/project1/assets/prop/Box",
            "/mnt/storage2/project1/textures/wood.tga",
            "/Volumes/storage1/project2/input/20190117",
            "/Volumes/storage2/project2/shots",
        ]
        remap = remapping.MixedPlatformRemap(input_mapping)
        result = remap(input_paths, "Mac")

        self.assertEqual(expected_result, result)

    def test_remap_with_paths_from_mixed_platforms_with_missing_target_platform_should_raise(
        self,
    ):
        input_mapping = {
            "Windows": ["L:\\", "P:\\", "G:\\"],
            "Linux": [
                "/mnt/storage1",
                "/mnt/storage2",
                "/mnt/storage3",
            ],
        }
        input_paths = [
            "L:\\temp",
            "p:/project1/textures\\grass.tga",
            "P:\\project1\\assets\\env\\Forest",
        ]
        target_platform = "Mac"
        remap = remapping.MixedPlatformRemap(input_mapping)

        with self.assertRaises(ValueError) as e:
            remap(input_paths, target_platform)

        self.assertEqual(
            f"Destination platform '{target_platform}' "
            f"was not specified in input mapping: {input_mapping}",
            str(e.exception),
        )

    def test_initialize_remap_mixed_platforms_with_different_paths_number_should_raise_error(
        self,
    ):
        input_mapping = {
            "Windows": ["L:\\", "P:\\"],
            "Linux": ["/mnt/storage1"],  # missing element
            "Mac": ["/Volumes/storage1", "/Volumes/storage2"],
        }
        with self.assertRaises(ValueError) as e:
            remapping.MixedPlatformRemap(input_mapping)

        self.assertEqual(
            f"Paths lists in mapping should have the same size. Given mapping: {input_mapping}",
            str(e.exception),
        )

    def test_initialize_remap_mixed_platforms_with_incorrect_mapping_format_should_raise(
        self,
    ):
        input_mapping = {
            "L:\\": "X:\\",
            "P:\\project1\\textures": "Z:\\library\\textures",
        }
        with self.assertRaises(ValueError) as e:
            remapping.MixedPlatformRemap(input_mapping)

        self.assertEqual(
            f"Incorrect format of input mapping: '{input_mapping}'. "
            f"Should be dict of str keys and list or tuple values.",
            str(e.exception),
        )
