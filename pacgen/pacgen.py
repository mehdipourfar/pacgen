import pprint
import sys
from urllib.parse import urlparse
import yaml


class PacGen:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        self.proxies = {
            k: self.parse_proxy(v) for k, v in data['proxies'].items()
        }
        self.proxies['DIRECT'] = 'DIRECT'
        self.routes = data['routes']

        for route in self.routes.values():
            if route not in self.proxies:
                print('ERROR: `{}` is not in the proxies list'.format(route))
                sys.exit(1)

        self.default_proxy = data['default_proxy']
        if self.default_proxy not in self.proxies:
            print('ERROR: `{}` is not in the proxies list'.format(
                self.default_proxy
            ))
            sys.exit(1)
        self.default_proxy = self.proxies[self.default_proxy]

        excludes = data.get('excludes', [])
        for route in excludes:
            self.routes[route] = 'DIRECT'

    @staticmethod
    def parse_proxy(proxy_url):
        proxy_url = proxy_url.strip()
        parsed_url = urlparse(proxy_url)
        scheme = {
            'http': 'HTTP',
            'https': 'HTTPS',
            'socks': 'SOCKS',
            'socks4': 'SOCKS4',
            'socks5': 'SOCKS5'
        }.get(parsed_url.scheme.lower(), 'SOCKS5')
        return '{} {}'.format(
            scheme,
            parsed_url.netloc
        )

    def generate_pac(self, output_path=None):
        pac = """
var proxies = {proxies};

var routes = {routes};

var defaultProxy = "{default_proxy}";

function FindProxyForURL(url, host) {{
    if (Object.hasOwnProperty.call(routes, host)) {{
        return proxies[routes[host]];
    }}

    var suffix, pos;
    pos = host.lastIndexOf('.');
    pos = host.lastIndexOf('.', pos - 1);
    while (1) {{
        if (pos <= 0) {{
            return defaultProxy;
        }}
        suffix = host.substring(pos + 1);
        if (Object.hasOwnProperty.call(routes, suffix)) {{
            return proxies[routes[suffix]];
        }}
        pos = host.lastIndexOf('.', pos - 1);
    }};
}};
        """.format(
            proxies=pprint.pformat(self.proxies),
            routes=pprint.pformat(self.routes),
            default_proxy=self.default_proxy
        )

        with open(output_path, 'w') as f:
            f.write(pac)
