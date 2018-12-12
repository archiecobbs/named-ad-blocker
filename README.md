# named-ad-blocker

**named-ad-blocker** is an RPM package for openSUSE that configures `named(8)` to block DNS requests to ad-serving sites.

**named-ad-blocker** updates the configuration of `named(8)` to reject all DNS requests for domains associated with ad-serving websites. This is done using the [response policy zone](https://dnsrpz.info/) support in BIND. By configuring `named(8)` as the DNS server for you network, you can enjoy a more ad-free browsing experience.

The list of domain names to block is updated regularly. The URL for the blacklist is configured in `/etc/sysconfig/named`.

