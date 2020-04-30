%define __jar_repack %{nil}
%define tomcat_home /usr/share/tomcat8
%define tomcat_group tomcat8
%define tomcat_user tomcat8
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
Source1:    tomcat8.init
Source2:    tomcat8.sysconfig
Source3:    tomcat8.logrotate
Source4:    tomcat8.conf
#Requires:   jdk
Requires:   java-1.8.0-headless
Requires:   redhat-lsb-core
Conflicts:  tomcat, tomcat6, tomcat7
BuildRoot:  %{_tmppath}/tomcat8-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Tomcat is the servlet container that is used in the official Reference
Implementation for the Java Servlet and JavaServer Pages technologies.
The Java Servlet and JavaServer Pages specifications are developed by
Sun under the Java Community Process.

Tomcat is developed in an open and participatory environment and
released under the Apache Software License. Tomcat is intended to be
a collaboration of the best-of-breed developers from around the world.
We invite you to participate in this open development project. To
learn more about getting involved, click here.

This package contains the base tomcat installation that depends on Sun's JDK and not
on JPP packages. This package has been modified for Boundless Server.

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

# Remove *.bat
rm -f %{buildroot}/%{tomcat_home}/bin/*.bat

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
install -d -m 755 %{buildroot}/var/log/tomcat8/
cd %{buildroot}/%{tomcat_home}/
ln -s /var/log/tomcat8/ logs
cd -

# Put conf in /etc/ and link back.
install -d -m 755 %{buildroot}/%{_sysconfdir}
mv %{buildroot}/%{tomcat_home}/conf %{buildroot}/%{_sysconfdir}/tomcat8
mkdir %{buildroot}/%{_sysconfdir}/tomcat8/server-opts
cd %{buildroot}/%{tomcat_home}/
ln -s %{_sysconfdir}/tomcat8 conf
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

# Drop sbin script
install -d -m 755 %{buildroot}/%{_sbindir}
install    -m 755 %_sourcedir/tomcat8.bin %{buildroot}/%{_sbindir}/tomcat8

# Drop init script
install -d -m 755 %{buildroot}/%{_initrddir}
install    -m 755 %_sourcedir/tomcat8.init %{buildroot}/%{_initrddir}/tomcat8

# Drop sysconfig script
install -d -m 755 %{buildroot}/%{_sysconfdir}/sysconfig/
install    -m 644 %_sourcedir/tomcat8.sysconfig %{buildroot}/%{_sysconfdir}/sysconfig/tomcat8

# Drop conf script
install    -m 644 %_sourcedir/tomcat8.conf %{buildroot}/%{_sysconfdir}/tomcat8

# Drop logrotate script
install -d -m 755 %{buildroot}/%{_sysconfdir}/logrotate.d
install    -m 644 %_sourcedir/tomcat8.logrotate %{buildroot}/%{_sysconfdir}/logrotate.d/tomcat8

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
/var/log/tomcat8/
%defattr(-,tomcat8,tomcat8)
%{tomcat_user_home}
%{tomcat_home}
%defattr(-,root,root)
%{_initrddir}/tomcat8
%{_sbindir}/tomcat8
%{_sysconfdir}/logrotate.d/tomcat8
%defattr(-,root,%{tomcat_group})
%{tomcat_cache_home}
%{tomcat_cache_home}/temp
%{tomcat_cache_home}/work
%{tomcat_user_home}/webapps
%config(noreplace) %{_sysconfdir}/sysconfig/tomcat8
%defattr(-,tomcat8,tomcat8)
%config(noreplace) %{_sysconfdir}/tomcat8/*

%post
if [ -f /sbin/chkconfig ]; then
  chkconfig --add tomcat8
elif [ -f /usr/sbin/update-rc.d ]; then
  if [ ! -f /etc/init.d/tomcat8 ]; then
    ln -s /etc/rc.d/init.d/tomcat8 /etc/init.d/tomcat8
  fi
#  update-rc.d tomcat8 defaults
fi
chown -R tomcat8:tomcat8 /etc/tomcat8

%preun
if [ $1 = 0 ]; then
  service tomcat8 stop > /dev/null 2>&1
  if [ -f /sbin/chkconfig ]; then
    chkconfig --del tomcat8
  elif [ -f /usr/sbin/update-rc.d ]; then
    update-rc.d -f tomcat8 remove
    unlink /etc/init.d/tomcat8
  fi
fi

%postun
#service tomcat8 restart >/dev/null 2>&1

%changelog
