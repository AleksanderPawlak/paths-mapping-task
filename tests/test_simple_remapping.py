import unittest

from src import remapping


class TestMapping(unittest.TestCase):
    def test_remap_paths_from_windows(self):
        input_mapping = {
            "L:\\": "X:\\",
            "P:\\project1\\textures": "Z:\\library\\textures",
        }
        input_paths = [
            "L:\\temp",
            "p:///////project1/textures\\grass.tga",
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
        remap = remapping.SimpleRemap(input_mapping)
        result = remap(input_paths)

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
        remap = remapping.SimpleRemap(input_mapping)
        result = remap(input_paths)

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
        remap = remapping.SimpleRemap(input_mapping)
        result = remap(input_paths)

        self.assertEqual(expected_result, result)

    def test_remap_paths_from_linux_with_parent_stmt_in_mapping(self):
        input_mapping = {
            "/mnt/storage1/": "/mnt2/../home/user/something/",
            "/mnt3/": "/mnt/",
        }
        input_paths = [
            "/mnt/storage1/temp",
            "/mnt3/storage1/",
            "cache/Tree.abc",
            "/mnt5/nope",
        ]
        expected_result = [
            "/home/user/something/temp",
            "/mnt/storage1",
            "cache/Tree.abc",
            "/mnt5/nope",
        ]
        remap = remapping.SimpleRemap(input_mapping)
        result = remap(input_paths)

        self.assertEqual(expected_result, result)
