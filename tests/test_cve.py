import unittest
import urllib

import predict.cve


class TestCVE(unittest.TestCase):

    def test_valid_cve_id(self):
        # Positive tests
        self.assertTrue(predict.cve.is_valid_cve_id("CVE-2014-4014"))

        # Weirder positive test
        self.assertTrue(predict.cve.is_valid_cve_id("CVE-2014-4014234"))

        # Negative tests
        self.assertFalse(predict.cve.is_valid_cve_id("CVD-2014-4014"))
        self.assertFalse(predict.cve.is_valid_cve_id("CVD-14-4014"))
        self.assertFalse(predict.cve.is_valid_cve_id("CVD-2014-401"))
        self.assertFalse(predict.cve.is_valid_cve_id("CVD-2014-40145678"))
        self.assertFalse(predict.cve.is_valid_cve_id("javascript: alert('hello')"))

    
    def test_valid_github_link(self):
        # Positive tests
        self.assertTrue(predict.cve.is_github_link(urllib.parse.urlparse("https://github.com/torvalds/linux/commit/23adbe12ef7d3d4195e80800ab36b37bee28cd03")))
        self.assertTrue(predict.cve.is_github_link(urllib.parse.urlparse("http://github.com/torvalds/linux/commit/23adbe12ef7d3d4195e80800ab36b37bee28cd03")))
        self.assertTrue(predict.cve.is_github_link(urllib.parse.urlparse("https://www.github.com/torvalds/linux/commit/23adbe12ef7d3d4195e80800ab36b37bee28cd03")))
        self.assertTrue(predict.cve.is_github_link(urllib.parse.urlparse("http://www.github.com/torvalds/linux/commit/23adbe12ef7d3d4195e80800ab36b37bee28cd03")))

        # Negative tests
        self.assertFalse(predict.cve.is_github_link(urllib.parse.urlparse("http://github.com/torvalds/linux/commit/23adbe12ef7d3d4195e80800ab36b37bee28cd03.diff")))
        self.assertFalse(predict.cve.is_github_link(urllib.parse.urlparse("http://github.com/torvalds/linux/commit/23adbe12ef7d3d4195e80800ab36b37bee28cd03.patch")))
        self.assertFalse(predict.cve.is_github_link(urllib.parse.urlparse("http://github.com/torvalds/linux/blame/23adbe12ef7d3d4195e80800ab36b37bee28cd03/fs/attr.c")))


    # TODO needs more testing
    def test_valid_git_link(self):
        # Positive test
        self.assertTrue(predict.cve.is_git_link(urllib.parse.urlparse("http://git.qemu.org/?p=qemu.git;a=commit;h=509a41bab5306181044b5fff02eadf96d9c8676a")))

        # Negative test
        self.assertFalse(predict.cve.is_git_link(urllib.parse.urlparse("https://git.qemu.org/?p=qemu.git;a=log;h=refs/tags/v4.1.0-rc4")))


    def test_get_nonexistent_cve(self):
        self.assertIsNone(predict.cve.get_cve("CVE-0000-0000"))