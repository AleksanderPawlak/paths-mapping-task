import unittest

from src import remapping


class TestMapping(unittest.TestCase):
    # TODO: test situation where all windows paths are relative and written with "\" separator
    def test_remap_paths_from_windows(self):
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
        remap = remapping.tools.SimpleRemap(input_mapping)
        result = remap(input_paths, remapping.tools.System.WINDOWS)

        self.assertEqual(expected_result, result)

    def test_remap_paths_from_linux(self):
        input_mapping = {
            "/mnt/storage1/": "/mnt2/storage2/",
            "/mnt3/": "/mnt/",
        }
        input_paths = [
            "/mnt/storage1/temp",
            "/mnt3/storage1/",
            "cache/Tree.abc",
            "/mnt5/nope",
        ]
        expected_result = [
            "/mnt2/storage2/temp",
            "/mnt/storage1",
            "cache/Tree.abc",
            "/mnt5/nope",
        ]
        remap = remapping.tools.SimpleRemap(input_mapping)
        result = remap(input_paths, remapping.tools.System.LINUX)

        self.assertEqual(expected_result, result)

    def test_remap_paths_from_mac(self):
        input_mapping = {
            "/Volumes/storage1/": "/Volumes/storage4/",
            "/Volumes/storage2": "/Volumes/storage3",
        }
        input_paths = [
            "/Volumes/storage1/project2/input/20190117",
            "/Volumes/storage2/project3/shots",
            "/Volumes/storage_0/project1/shots",
        ]
        expected_result = [
            "/Volumes/storage4/project2/input/20190117",
            "/Volumes/storage3/project3/shots",
            "/Volumes/storage_0/project1/shots",
        ]
        remap = remapping.tools.SimpleRemap(input_mapping)
        result = remap(input_paths, remapping.tools.System.MAC)

        self.assertEqual(expected_result, result)

    def test_remap_paths_with_unsupported_platform_should_raise(self):
        input_mapping = {
            "/mnt/storage1/": "/mnt2/storage2/",
            "/mnt3/": "/mnt/",
        }
        input_paths = [
            "/mnt/storage1/temp",
            "/mnt3/storage1/",
            "cache/Tree.abc",
            "/mnt5/nope",
        ]
        dummy_platform = "SomeDummyPlatform"
        remap = remapping.tools.SimpleRemap(input_mapping)

        with self.assertRaises(ValueError) as e:
            remap(input_paths, dummy_platform)

        self.assertEqual(
            f"Passed platform: '{dummy_platform}' is not supported.",
            str(e.exception),
        )

    def test_remap_paths_from_different_platforms(self):
        input_mapping = {
            remapping.tools.System.WINDOWS: ["L:\\", "P:\\"],
            remapping.tools.System.MAC: ["/Volumes/storage1", "/Volumes/storage2/"],
        }
        input_paths = [
            "L:\\temp",
            "p:/project1/textures\\grass.tga",
            "P:\\project1\\assets\\env\\Forest",
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
        remap = remapping.tools.MixedPlatformRemap(input_mapping)
        result = remap(input_paths, remapping.tools.System.MAC)

        self.assertEqual(expected_result, result)

    def test_remap_from_mixed_platforms(self):
        input_mapping = {
            remapping.tools.System.WINDOWS: ["L:\\", "P:\\"],
            remapping.tools.System.LINUX: ["/mnt/storage1", "/mnt/storage2"],
            remapping.tools.System.MAC: ["/Volumes/storage1", "/Volumes/storage2"],
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
            # "cache/Tree.abc",  # This might be a bug in specification
            "cache\\Tree.abc",
            "g:\\nope",
            "/mnt/storage2/project1/assets/prop/Box",
            "/mnt/storage2/project1/textures/wood.tga",
            "/mnt/storage1/project2/input/20190117",
            "/mnt/storage1/project2/shots",
        ]
        remap = remapping.tools.MixedPlatformRemap(input_mapping)
        result = remap(input_paths, remapping.tools.System.LINUX)

        self.assertEqual(expected_result, result)

    def test_remap_paths_from_mixed_platforms_with_none_value_in_mappings_source(self):
        input_mapping = {
            remapping.tools.System.WINDOWS: ["L:\\", "P:\\", "G:\\"],
            remapping.tools.System.LINUX: [
                "/mnt/storage1",
                "/mnt/storage2",
                "/mnt/storage3",
            ],
            remapping.tools.System.MAC: [
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
        remap = remapping.tools.MixedPlatformRemap(input_mapping)
        result = remap(input_paths, remapping.tools.System.LINUX)

        self.assertEqual(expected_result, result)

    def test_remap_paths_from_mixed_platforms_with_none_value_in_mappings_dst(self):
        """ "
        If we want to reuse mapping there might be case where there is None value in dst paths.
        """
        input_mapping = {
            remapping.tools.System.WINDOWS: ["L:\\", "P:\\", "G:\\"],
            remapping.tools.System.LINUX: [
                "/mnt/storage1",
                "/mnt/storage2",
                "/mnt/storage3",
            ],
            remapping.tools.System.MAC: [
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
            "/Volumes/storage1/temp",
            "p:/project1/textures\\grass.tga",
            "P:\\project1\\assets\\env\\Forest",
            # "cache/Tree.abc",  # This might be a bug in specification. Why should it change?
            "cache\\Tree.abc",
            "/Volumes/storage2/yes",
            "/mnt/storage2/project1/assets/prop/Box",
            "/mnt/storage2/project1/textures/wood.tga",
            "/Volumes/storage1/project2/input/20190117",
            "/Volumes/storage2/project2/shots",
        ]
        remap = remapping.tools.MixedPlatformRemap(input_mapping)
        result = remap(input_paths, remapping.tools.System.MAC)

        self.assertEqual(expected_result, result)

    def test_remap_with_paths_from_mixed_platforms_with_missing_target_platform_should_raise(
        self,
    ):
        input_mapping = {
            remapping.tools.System.WINDOWS: ["L:\\", "P:\\", "G:\\"],
            remapping.tools.System.LINUX: [
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
        target_platform = remapping.tools.System.MAC
        remap = remapping.tools.MixedPlatformRemap(input_mapping)

        with self.assertRaises(ValueError) as e:
            remap(input_paths, target_platform)

        self.assertEqual(
            f"Destination platform '{target_platform}' "
            f"was not specified in input mapping: {input_mapping}",
            str(e.exception),
        )

    def test_remap_with_paths_from_mixed_platforms_with_unsupported_platform_should_raise(
        self,
    ):
        dummy_platform = "SomeDummyPlatform"
        input_mapping = {
            remapping.tools.System.WINDOWS: ["L:\\", "P:\\"],
            dummy_platform: ["/mnt/storage1", "/mnt/storage2"],
        }
        input_paths = [
            "L:\\temp",
            "p:/project1/textures\\grass.tga",
            "P:\\project1\\assets\\env\\Forest",
        ]
        remap = remapping.tools.MixedPlatformRemap(input_mapping)

        with self.assertRaises(ValueError) as e:
            remap(input_paths, dummy_platform)

        self.assertEqual(
            f"Passed platform: '{dummy_platform}' is not supported.",
            str(e.exception),
        )

    def test_initialize_remap_mixed_platforms_with_different_paths_number_should_raise_error(
        self,
    ):
        input_mapping = {
            remapping.tools.System.WINDOWS: ["L:\\", "P:\\"],
            remapping.tools.System.LINUX: ["/mnt/storage1"],  # missing element
            remapping.tools.System.MAC: ["/Volumes/storage1", "/Volumes/storage2"],
        }
        with self.assertRaises(ValueError) as e:
            remapping.tools.MixedPlatformRemap(input_mapping)

        self.assertEqual(
            f"Paths lists in mapping should have the same size. Given mapping: {input_mapping}",
            str(e.exception),
        )

    # TODO: test other failing cases
    # def test_incorrect_remap_path_types(self):  # TODO: is this valid?
    #     ...
