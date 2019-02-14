from urllib.parse import urlparse
import yaml


class PacGen:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            data = yaml.load(f)
        self.proxies = {
            k: self.parse_proxy(v) for k, v in data['proxies'].items()
        }
        self._default_proxy = data['default_proxy']
        self.excludes = data.get('excludes', [])
        assert self._default_proxy in self.proxies
        self.routes = data['routes']
        for route in self.routes.values():
            assert route in self.proxies

    @staticmethod
    def parse_proxy(proxy_url):
        if proxy_url.lower() == 'direct':
            return 'DIRECT'
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

    @property
    def default_proxy(self):
        return self.proxies[self._default_proxy]

    def get_route_condition(self, route):
        proxy = self.proxies[self.routes[route]]
        return """
          if (host === '{route}') {{
            return '{proxy}';
          }}""".format(route=route, proxy=proxy)

    def get_exclude_condition(self, excluded_url):
        return """
          if (dnsDomainIs(host, '{excluded_url}')) {{
            return 'DIRECT';
          }}""".format(excluded_url=excluded_url)

    def generate_pac(self, output):
        route_conditions = ''.join(
            map(self.get_route_condition, self.routes)
        )
        exclude_conditions = ''.join(
            map(self.get_exclude_condition, self.excludes)
        )
        pac = """
        function FindProxyForURL(url, host) {{
            {exclude_conditions}
            {route_conditions}
          return '{default_proxy}';
        }}""".format(
            exclude_conditions=exclude_conditions,
            route_conditions=route_conditions,
            default_proxy=self.default_proxy
        ).strip()
        with open(output, 'w') as f:
            f.write(pac)
