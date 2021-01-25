%define __jar_repack %{nil}
%define tomcat_home /usr/share/tomcat8
%define tomcat_group tomcat
%define tomcat_user tomcat
%define tomcat_user_home /var/lib/tomcat8
%define tomcat_cache_home /var/cache/tomcat8

Summary:    Apache Servlet/JSP Engine, RI for Servlet 3.1/JSP 2.3 API
Name:       tomcat8
Version:    8.5.54
BuildArch:  noarch
Release:    1%{?dist}
License:    Apache Software License
Group:      Networking/Daemons
URL:        http://tomcat.apache.org/
Source0:    http://archive.apache.org/dist/tomcat/tomcat-8/v%{version}/bin/apache-tomcat-%{version}.tar.gz
Source1:    tomcat8.logrotate
Source2:    setenv.sh
Requires:   java-11-openjdk-headless
Requires:   redhat-lsb-core
BuildRequires: systemd systemd-rpm-macros
Conflicts:  tomcat, tomcat6, tomcat7
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Tomcat is the servlet container that is used in the official Reference
Implementation for the Java Servlet and JavaServer Pages technologies.
The Java Servlet and JavaServer Pages specifications are developed by
Sun under the Java Community Process.

Tomcat is developed in an open and participatory environment and
released under the Apache Software License. Tomcat is intended to be
a collaboration of the best-of-breed developers from around the world.

%prep
%setup -q -n apache-tomcat-%{version}

%build

%install
install -d -m 755 %{buildroot}/%{tomcat_home}/
cp -R * %{buildroot}/%{tomcat_home}/

# Remove all webapps. Put webapps in /var/lib and link back.
rm -rf %{buildroot}/%{tomcat_home}/webapps
install -d -m 775 %{buildroot}%{tomcat_user_home}/webapps
cd %{buildroot}/%{tomcat_home}/
ln -s %{tomcat_user_home}/webapps webapps
chmod 775 %{buildroot}/%{tomcat_user_home}
cd -

rm -f %{buildroot}/%{tomcat_home}/bin/*.bat
chmod 755 %{buildroot}/%{tomcat_home}/bin/*.sh

# Remove extra logging configs
sed -i -e '/^3manager/d' -e '/\[\/manager\]/d' \
    -e '/^4host-manager/d' -e '/\[\/host-manager\]/d' \
    -e '/^java.util.logging.ConsoleHandler/d' \
    -e 's/, *java.util.logging.ConsoleHandler//' \
    -e 's/, *4host-manager.org.apache.juli.AsyncFileHandler//' \
    -e 's/, *3manager.org.apache.juli.AsyncFileHandler//' \
    %{buildroot}/%{tomcat_home}/conf/logging.properties

# Put logging in /var/log and link back.
rm -rf %{buildroot}/%{tomcat_home}/logs
install -d -m 755 %{buildroot}/var/log/%{name}/
cd %{buildroot}/%{tomcat_home}/
ln -s /var/log/%{name}/ logs
cd -

# Put conf in /etc/ and link back.
install -d -m 755 %{buildroot}/%{_sysconfdir}
mv %{buildroot}/%{tomcat_home}/conf %{buildroot}/%{_sysconfdir}/%{name}
mkdir %{buildroot}/%{_sysconfdir}/%{name}/server-opts
cd %{buildroot}/%{tomcat_home}/
ln -s %{_sysconfdir}/%{name} conf
cd -

# Put temp and work to /var/cache and link back.
install -d -m 775 %{buildroot}%{tomcat_cache_home}
mv %{buildroot}/%{tomcat_home}/temp %{buildroot}/%{tomcat_cache_home}/
mv %{buildroot}/%{tomcat_home}/work %{buildroot}/%{tomcat_cache_home}/
cd %{buildroot}/%{tomcat_home}/
ln -s %{tomcat_cache_home}/temp
ln -s %{tomcat_cache_home}/work
chmod 775 %{buildroot}/%{tomcat_cache_home}/temp
chmod 775 %{buildroot}/%{tomcat_cache_home}/work
cd -

# Drop logrotate script
install -d -m 755 %{buildroot}/%{_sysconfdir}/logrotate.d
install    -m 644 %{SOURCE1} %{buildroot}/%{_sysconfdir}/logrotate.d/%{name}

%{__install} -m 644 %_sourcedir/server.xml %{buildroot}/%{_sysconfdir}/%{name}

# Environment setup script
install    -m 755 %{SOURCE2} %{buildroot}/%{tomcat_home}/bin

# Systemd service configuration
%{__mkdir_p} %{buildroot}%{_unitdir}
install    -m 644 %{_sourcedir}/%{name}.service %{buildroot}%{_unitdir}

%clean
rm -rf %{buildroot}

%pre
mkdir -p /var/lock/subsys/
if [ ! -f /sbin/chkconfig ] && [ ! -f /usr/sbin/update-rc.d ]; then
  echo "Service handler not found, abort"
  exit 1
fi
getent group %{tomcat_group} >/dev/null || groupadd -r %{tomcat_group}
getent passwd %{tomcat_user} >/dev/null || /usr/sbin/useradd --comment "Tomcat 8 Daemon User" --shell /bin/bash -M -r -g %{tomcat_group} --home %{tomcat_home} %{tomcat_user}

%files
%defattr(-,%{tomcat_user},%{tomcat_group})
/var/log/%{name}/
%{tomcat_user_home}
%{tomcat_home}
%defattr(-,root,root)
%{_sysconfdir}/logrotate.d/%{name}
%defattr(-,root,%{tomcat_group})
%{tomcat_cache_home}
%{tomcat_cache_home}/temp
%{tomcat_cache_home}/work
%{tomcat_user_home}/webapps
%defattr(-,%{tomcat_user},%{tomcat_group})
%config(noreplace) %{_sysconfdir}/%{name}/*
%{_unitdir}/%{name}.service

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%changelog
