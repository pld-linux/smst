%include	/usr/lib/rpm/macros.perl
Summary:	SMS Transport - Jabber to SMS gateway
Summary(pl):	Bramka z Jabbera do SMS
Name:		smst
Version:	R4
Release:	1
License:	GPL
Group:		Applications/Communications
Source0:	http://www.jabberstudio.org/files/sms-transport/%{name}-%{version}.tar.gz
# Source0-md5:	ff25330ccee0faf52ea343f906ce1846
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-external_config.patch
Patch1:		%{name}-default_config.patch
URL:		http://www.jabberstudio.org/projects/sms-transport
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
Requires:	daemon
Requires:	jabber-common
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Jabber server component that enables users to send Short Messages to
Cellular phones (popular SMS) using operator's web services.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
awk '
BEGIN { config=0; }

/# END [A-Z ]*CONFIGURATION/ { print; config=0; }
	{ if (config==1) print; }
/# BEGIN [A-Z ]*CONFIGURATION/ { print; config=1; }
' smst.pl > smst.rc

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/jabber,%{_sbindir}} \
	$RPM_BUILD_ROOT{/etc/rc.d/init.d,/etc/sysconfig,/var/log,/var/lib/smst}

install smst.pl $RPM_BUILD_ROOT%{_sbindir}/smst
install smst.rc $RPM_BUILD_ROOT%{_sysconfdir}/jabber/smst.rc
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/smst
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/smst
touch $RPM_BUILD_ROOT/var/log/smst.log

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /etc/jabber/secret ] ; then
	SECRET=`cat /etc/jabber/secret`
	if [ -n "$SECRET" ] ; then
        	echo "Updating component authentication secret in smst.rc..."
		perl -pi -e "s/'secret'/'$SECRET'/" /etc/jabber/smst.rc
	fi
fi

/sbin/chkconfig --add smst
if [ -r /var/lock/subsys/smst ]; then
	/etc/rc.d/init.d/smst restart >&2
else
	echo "Run \"/etc/rc.d/init.d/smst start\" to start Janchor."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -r /var/lock/subsys/smst ]; then
		/etc/rc.d/init.d/smst stop >&2
	fi
	/sbin/chkconfig --del smst
fi

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/*
%attr(640,root,jabber) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/jabber/smst.rc
%attr(754,root,root) /etc/rc.d/init.d/smst
%config(noreplace) %verify(not size mtime md5) /etc/sysconfig/smst
%attr(664,root,jabber) /var/log/smst.log
%dir %attr(775,root,jabber) /var/lib/smst
