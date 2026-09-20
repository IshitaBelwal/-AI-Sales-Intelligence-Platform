WEB_PRODUCTS = {
    "nginx",
    "apache httpd",
    "microsoft iis httpd",
    "openresty",
    "caddy",
    "litespeed",
    "litespeed httpd",
    "cloudfront httpd",
    "cloudflare",
    "tengine",
    "lighttpd",
    "microsoft httpapi httpd",
    "jetty",
    "boa web server",
    "apache tomcat",
}


REMOTE_ACCESS_PRODUCTS = {
    "openssh",
    "vnc",
    "remote desktop protocol",
    "windows terminal server",
    "winrm",
    "microsoft windows rpc over http",
    "microsoft rpc endpoint mapper",
    "pptp",
}


EMAIL_PRODUCTS = {
    "postfix smtpd",
    "exim smtpd",
    "postfix",
    "exim",
}


PROXY_PRODUCTS = {
    "squid http proxy",
    "socks4a",
    "ncat http proxy",
    "ezproxy web proxy",
    "dircproxy",
}


NETWORK_PRODUCTS = {
    "mikrotik",
    "mikrotik bandwidth-test server",
    "mikrotik winbox",
    "net-snmp",
    "bigip",
    "cisco ip sla",
    "ciscosystems",
}


CDN_PRODUCTS = {
    "cloudfront httpd",
    "cloudflare",
    "akamaighost",
}


LOAD_BALANCER_PRODUCTS = {
    "aws elb",
    "bigip",
    "microsoft azure application gateway",
    "citrix netscaler",
}


DATABASE_PRODUCTS = {
    "mysql",
    "mariadb",
    "postgresql",
}


IOT_PRODUCTS = {
    "hikvision ip camera",
    "dahua xvr",
    "dahua nvr",
    "dahua dvr",
    "dahua-based dvr",
    "asus wireless router rt-ax68u",
    "asus aicloud",
    "chromecast",
}


CONTAINER_PLATFORM_PRODUCTS = {
    "kubernetes",
    "istio service mesh",
    "portainer",
}


SECURITY_NETWORK_PRODUCTS = {
    "sonicwall",
    "sophos ssl vpn user portal",
}


OBSERVABILITY_PRODUCTS = {
    "prometheus node exporter",
}


FILE_TRANSFER_PRODUCTS = {
    "pure-ftpd",
    "vsftpd",
}


def normalize_product(product):
    if product is None:
        return None

    if not isinstance(product, str):
        return None

    product = product.strip().lower()

    if not product:
        return None

    return product


def classify_product(product):
    product = normalize_product(product)

    if product is None:
        return "UNKNOWN"

    if product in WEB_PRODUCTS:
        return "WEB"

    if product in REMOTE_ACCESS_PRODUCTS:
        return "REMOTE_ACCESS"

    if product in EMAIL_PRODUCTS:
        return "EMAIL"

    if product in PROXY_PRODUCTS:
        return "PROXY"

    if product in NETWORK_PRODUCTS:
        return "NETWORK"

    if product in CDN_PRODUCTS:
        return "CDN"

    if product in LOAD_BALANCER_PRODUCTS:
        return "LOAD_BALANCER"

    if product in DATABASE_PRODUCTS:
        return "DATABASE"

    if product in IOT_PRODUCTS:
        return "IOT"

    if product in CONTAINER_PLATFORM_PRODUCTS:
        return "CONTAINER_PLATFORM"

    if product in SECURITY_NETWORK_PRODUCTS:
        return "SECURITY_NETWORK"

    if product in OBSERVABILITY_PRODUCTS:
        return "OBSERVABILITY"

    if product in FILE_TRANSFER_PRODUCTS:
        return "FILE_TRANSFER"

    return "OTHER"