"""
项目基础测试框架

本模块为项目建立基础的测试框架和测试规范，确保后续每个阶段的代码都有对应的单元测试支撑。
选用Python标准库中的unittest模块作为测试框架，无需引入外部测试依赖。

设计原则：
- 零外部依赖：仅使用Python标准库unittest
- 命名规范：测试文件以test_开头，测试类以Test开头，测试方法以test_开头
- 基础工具类：封装常用的断言方法和测试辅助功能
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class BaseTestCase(unittest.TestCase):
    """
    基础测试用例类

    所有系统测试用例的基类，提供常用的断言方法和测试辅助功能。
    """

    def assertIsNotNone(self, obj, msg=None):
        """断言对象不为None"""
        super().assertIsNotNone(obj, msg)

    def assertIsInstance(self, obj, cls, msg=None):
        """断言对象是某个类的实例"""
        super().assertIsInstance(obj, cls, msg)

    def assertInRange(self, value, min_val, max_val, msg=None):
        """
        断言值在指定范围内

        Args:
            value: 要检查的值
            min_val: 最小值
            max_val: 最大值
            msg: 可选的断言消息
        """
        self.assertGreaterEqual(value, min_val, msg)
        self.assertLessEqual(value, max_val, msg)

    def assertFileExists(self, filepath, msg=None):
        """
        断言文件存在

        Args:
            filepath: 文件路径
            msg: 可选的断言消息
        """
        self.assertTrue(os.path.exists(filepath), msg or f"文件不存在: {filepath}")

    def assertDirectoryExists(self, dirpath, msg=None):
        """
        断言目录存在

        Args:
            dirpath: 目录路径
            msg: 可选的断言消息
        """
        self.assertTrue(os.path.isdir(dirpath), msg or f"目录不存在: {dirpath}")

    def assertIsCallable(self, obj, msg=None):
        """
        断言对象是可调用的

        Args:
            obj: 要检查的对象
            msg: 可选的断言消息
        """
        self.assertTrue(callable(obj), msg or f"对象不可调用: {obj}")


class TestFrameworkValidation(BaseTestCase):
    """测试框架自身验证"""

    def test_framework_import(self):
        """验证unittest框架可正常导入"""
        self.assertIsNotNone(unittest)

    def test_base_test_case_exists(self):
        """验证基础测试类存在"""
        self.assertIsNotNone(BaseTestCase)

    def test_assert_in_range(self):
        """验证范围断言方法"""
        self.assertInRange(5, 1, 10)
        self.assertInRange(0.5, 0.0, 1.0)

    def test_assert_file_exists(self):
        """验证文件存在断言"""
        self.assertFileExists(__file__)

    def test_assert_directory_exists(self):
        """验证目录存在断言"""
        self.assertDirectoryExists(os.path.dirname(__file__))


def run_tests(test_pattern="test_*.py"):
    """
    运行测试

    Args:
        test_pattern: 测试文件匹配模式

    Returns:
        unittest.TestResult: 测试结果
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    start_dir = os.path.dirname(os.path.abspath(__file__))
    discover = loader.discover(start_dir, pattern=test_pattern)
    suite.addTests(discover)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
