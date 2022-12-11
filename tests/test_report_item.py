import unittest
import copy

from modules.report_item import ReportItem
from modules.line_attrs import LineAttrs


class TestReportItem(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._example_line: str = \
            '1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] ' \
            '"GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" ' \
            '"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" ' \
            '"-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390'
        cls._example_line_attrs = LineAttrs(text_line=cls._example_line)
        cls._report_item = ReportItem.from_line_attrs(
            line_attrs=cls._example_line_attrs,
        )

    def test_1_first_item(self) -> None:
        self.assertEqual(self._report_item.count, 1)

    def test_2_append(self) -> None:
        self._report_item.append(self._example_line_attrs)
        self.assertEqual(self._report_item.count, 2)

    def test_calculate(self) -> None:
        self._report_item.times = [1., 1., 7., 3., 3.]
        self._report_item.count = len(self._report_item.times)
        self._report_item.calculate()
        self.assertEqual(self._report_item.time_avg, 3.0)
        self.assertEqual(self._report_item.time_max, 7.)
        self.assertEqual(self._report_item.time_med, 3.0)

    def test_str(self) -> None:
        self.assertRegex(
            str(self._report_item),
            r'^"count":\d+,"count_perc":[\d\.]+,"time_sum":[\d\.]+,' +
            r'"time_perc":[\d\.]+,"time_avg":[\d\.]+,"time_max":[\d\.]+,' +
            r'"time_med":[\d\.]+$'
        )

    def test_gt(self) -> None:
        prev_item: ReportItem = copy.copy(self._report_item)
        self._report_item.append(self._example_line_attrs)
        self.assertGreater(self._report_item, prev_item)


if __name__ == '__main__':
    unittest.main()
