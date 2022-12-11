import unittest

from modules import LineAttrs


class TestLineAttrs(unittest.TestCase):
    def test_get_template_is_empty(self) -> None:
        example_line: str = \
            'invalid 1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] ' \
            '"GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" ' \
            '"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" ' \
            '"-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390'
        line_attrs: LineAttrs = LineAttrs(text_line=example_line)
        self.assertEqual(line_attrs.is_empty, True)

    def test_get_template_as_vars(self) -> None:
        example_line: str = \
            '1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] ' \
            '"GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" ' \
            '"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" ' \
            '"-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390'
        line_attrs: LineAttrs = LineAttrs(text_line=example_line)
        expected_vars: dict = {
            'remote_addr': '1.196.116.32',
            'remote_user': '- ',
            'http_x_real_ip': '-',
            'time_local': '29/Jun/2017:03:50:22 +0300',
            'type': 'GET',
            'request': '/api/v2/banner/25019354',
            'proto': 'HTTP/1.1',
            'status': '200',
            'body_bytes_sent': '927',
            'http_referer': '-',
            'http_user_agent': 'Lynx/2.8.8dev.9 libwww-FM/2.14 '
                               'SSL-MM/1.4.1 GNUTLS/2.10.5',
            'http_x_forwarded_for': '-',
            'http_X_REQUEST_ID': '1498697422-2190034393-4708-9752759',
            'http_X_RB_USER': 'dc7161be3',
            'request_time': '0.390',
        }
        self.assertEqual(vars(line_attrs), expected_vars)
        self.assertEqual(line_attrs.is_empty, False)


if __name__ == '__main__':
    unittest.main()
