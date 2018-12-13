# named-ad-blocker

**named-ad-blocker** configures `named(8)` to block DNS requests for ad-serving websites.

After installation, `named(8)` will respond with "unknown domain" to any request
for a domain on a configurable list of domains that are known to primarily serve
website advertisements. By configuring `named(8)` as the DNS server for you network,
you can enjoy a more ad-free web browsing experience.

**named-ad-blocker** relies on the response policy zone support in `named(8)`.

The list of domain names to block is automatically updated regularly on a weekly
basis, or at any time via `/usr/lib/named-ad-blocker/named-ad-blocker-update`.

The URL for the blacklist is configured in `/etc/sysconfig/named`.
