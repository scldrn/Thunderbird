import unittest
from tools.compare_legacy_results import compare


class ComparisonTests(unittest.TestCase):
    def test_shared_values_and_schema_are_compared_independently(self):
        result = compare({'rows': [{'x': 1.0, 'label': 'a'}]},
                         {'rows': [{'x': 1.0 + 1e-11, 'label': 'b', 'extra': 4}]})
        self.assertEqual(result['numeric_compared'], 1)
        self.assertEqual(result['numeric_outside_tolerance'], 0)
        self.assertEqual(result['added_fields'], ['/rows/0/extra'])
        self.assertEqual(result['other_differences'][0]['path'], '/rows/0/label')

    def test_numeric_changes_removals_and_lengths_are_reported(self):
        result = compare({'rows': [{'x': '1.0'}, {'x': '2'}], 'gone': True},
                         {'rows': [{'x': '1.1'}]})
        self.assertEqual(result['removed_fields'], ['/gone'])
        self.assertEqual(result['numeric_outside_tolerance'], 1)
        self.assertEqual(result['max_absolute_difference']['path'], '/rows/0/x')
        self.assertEqual(result['other_differences'][0]['old_length'], 2)

    def test_boolean_and_nonfinite_are_not_numeric(self):
        result = compare({'a': True, 'b': 'nan'}, {'a': False, 'b': 'inf'})
        self.assertEqual(result['numeric_compared'], 0)
        self.assertEqual(len(result['other_differences']), 2)


if __name__ == '__main__':
    unittest.main()
