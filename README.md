# PacGen: Pac file generator written in Python
If you use multiple proxies and you want to define rules to set specific proxy per specific host, this package can help you.
Simply create a ~/.pacgen.yml config file and define your rules there.
After that run updatepac command in your terminal and it will create ~/.proxy.pac

# Installation
```
    pip install pacgen
```


# Sample ~/.pacgen.yml
```
proxies:
  ssh_tunnel: socks5://127.0.0.1:1081
  shadowsocks: socks5://127.0.0.1:1080
  httpproxy: http://127.0.0.1:1082
routes:
  172.19.20.10: ssh_tunnel
  youtube.com: shadowsocks
  viemo.com: shadowsocks
  news.com: httpproxy
# default_proxy will be used for hosts which are not defined in routes.
default_proxy: shadowsocks
# here we define hosts that we don't want to use proxy for them.
excludes:
  - bank.com
  - lastpass.com
```
