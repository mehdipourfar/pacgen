import pprint
import sys
from urllib.parse import urlparse
import yaml


pac_template = """
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
}};"""


class PacGen:
    ALLOWED_SCHEMES = ['HTTP', 'HTTPS', 'SOCKS', 'SOCKS4', 'SOCKS5']

    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        self.proxies = {
            name: self.parse_proxy(addr)
            for name, addr in data['proxies'].items()
        }
        self.proxies['DIRECT'] = 'DIRECT'

        self.routes = data['routes']
        for route in self.routes.values():
            if route not in self.proxies:
                print('ERROR: `{}` is not in the proxies list'.format(route))
                sys.exit(1)

        try:
            self.default_proxy = self.proxies[data['default_proxy']]
        except KeyError:
            print('ERROR: `{}` is not in the proxies list'.format(
                data['default_proxy']
            ))
            sys.exit(1)

        for route in data.get('excludes', []):
            self.routes[route] = 'DIRECT'

    @staticmethod
    def parse_proxy(proxy_url):
        proxy_url = proxy_url.strip()
        parsed_url = urlparse(proxy_url)
        scheme = parsed_url.scheme.upper()
        if scheme not in PacGen.ALLOWED_SCHEMES:
            print('ERROR: Unknown scheme `{}`'.format(scheme))
            sys.exit(1)
        return '{} {}'.format(scheme, parsed_url.netloc)

    def generate_pac(self, output_path):
        pac = pac_template.format(
            proxies=pprint.pformat(self.proxies),
            routes=pprint.pformat(self.routes),
            default_proxy=self.default_proxy
        )
        with open(output_path, 'w') as f:
            f.write(pac)
