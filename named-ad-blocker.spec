#
# spec file for package named-ad-blocker
#
# Copyright (c) 2018 SUSE LINUX GmbH, Nuernberg, Germany.
# Copyright (C) 2018 Archie L. Cobbs. All rights reserved.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

%define sysconfigfile   %{_sysconfdir}/sysconfig/named
%define namedchroot     %{_var}/lib/named
%define namedconf       %{_sysconfdir}/named.conf
%define nameddir        %{_sysconfdir}/named.d
%define zonefilepath    master/%{name}.zone
%define zonefile        %{namedchroot}/%{zonefilepath}
%define zoneid          %{name}-zone

#Compat macro for new _fillupdir macro introduced in Nov 2017
%if ! %{defined _fillupdir}
    %define _fillupdir /var/adm/fillup-templates
%endif

Name:           named-ad-blocker
Version:        0.0.3
Release:        0
Summary:        Configures named(8) to block DNS requests for ad-serving websites
License:        Apache-2.0
Group:          Productivity/Networking/DNS
Source:         %{name}-%{version}.tar.gz
Url:            https://github.com/archiecobbs/%{name}/
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
Recommends:     cron
Requires(post): bind >= 9.8
Requires(post): bind-chrootenv
Requires:       curl
Requires(post): %fillup_prereq
Requires:       sed
%systemd_requires

%description
%{name} configures named(8) to block DNS requests for ad-serving websites.

After installation, named(8) will respond with "unknown domain" to any request
for a domain on a configurable list of domains that are known to primarily serve
website advertisements. By configuring named(8) as the DNS server for you network,
you can enjoy a more ad-free web browsing experience.

%{name} relies on the response policy zone support in named(8).

The list of domain names to block is automatically updated regularly on a weekly
basis, or at any time via %{_usr}/lib/%{name}/%{name}-update.

The URL for the blacklist is configured in %{sysconfigfile}.

%prep
%setup -q

%build

# Substitute macros
for FILE in %{name}-update %{name}.conf; do
    sed -r \
      -e 's|@pkgname@|%{name}|g' \
      -e 's|@sysconfigfile@|%{sysconfigfile}|g' \
      -e 's|@zonefile@|%{zonefile}|g' \
      -e 's|@zonefilepath@|%{zonefilepath}|g' \
      -e 's|@zoneid@|%{zoneid}|g' \
      < "${FILE}.in" > "${FILE}"
done

%install

# updater script
install -d %{buildroot}%{_usr}/lib/%{name}
install %{name}-update %{buildroot}%{_usr}/lib/%{name}/

# named include file
install -d %{buildroot}%{nameddir}
install %{name}.conf %{buildroot}%{nameddir}/

# sysconfig template
install -d %{buildroot}%{_fillupdir}
install %{name}.sysconfig %{buildroot}%{_fillupdir}/sysconfig.named-%{name}

# updater cron script
install -d %{buildroot}%{_sysconfdir}/cron.weekly
printf '#!/bin/bash\n\nexec %{_usr}/lib/%{name}/%{name}-update\n' > %{buildroot}%{_sysconfdir}/cron.weekly/%{name}

# docs
install -d %{buildroot}%{_datadir}/doc/packages/%{name}
install LICENSE %{buildroot}%{_datadir}/doc/packages/%{name}/

%post

# Install sysconfig stuff
%{fillup_only -an named}

# Apply patch on install
if [ "$1" -eq 1 ]; then

    # Create initial placeholder zonefile
    echo doubleclick.net | %{_usr}/lib/%{name}/%{name}-update -f -

    # Patch /etc/sysconfig/named
    sed -ri 's/^(NAMED_CONF_INCLUDE_FILES=["'\''])(.*)$/\1%{name}.conf \2/g' '%{sysconfigfile}'

    # Patch named.conf
    sed -ri '/^options/a        # THE FOLLOWING LINE ADDED BY %{name}\n\tresponse-policy { zone "%{zoneid}"; };' %{namedconf}

    # Reload named
    if systemctl -q is-active named.service; then
        systemctl reload-or-try-restart named.service
    fi

    # Notify about initializing blacklist
    echo "Note: you can initialize your DNS blacklist via %{_usr}/lib/%{name}/%{name}-update"
fi

%preun

# Clean up on uninstall
if [ "$1" -eq 0 ]; then

    # Unpatch named.conf
    sed -ri '/^[[:space:]]*# THE FOLLOWING LINE ADDED BY %{name}$/,+1d' %{namedconf}

    # Unpatch /etc/sysconfig/named
    sed -ri 's/^(NAMED_CONF_INCLUDE_FILES=.*)%{name}.conf ?(.*)$/\1\2/g' '%{sysconfigfile}'

    # Reload named
    if systemctl -q is-active named.service; then
        systemctl reload-or-try-restart named.service
    fi
fi

%files
%attr(0755,root,root) %{_usr}/lib/%{name}
%config %attr(0644,root,root) %{nameddir}/%{name}.conf
%config %attr(0755,root,root) %{_sysconfdir}/cron.weekly/%{name}
%attr(0644,root,root) %{_fillupdir}/sysconfig.named-%{name}
%doc %attr(0644,root,root) %{_datadir}/doc/packages/%{name}

%changelog
