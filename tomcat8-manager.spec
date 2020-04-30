%define __jar_repack %{nil}
%define tomcat_home /usr/share/tomcat8
%define tomcat_group tomcat8
%define tomcat_user tomcat8
%define tomcat_user_home /var/lib/tomcat8
%define tomcat_cache_home /var/cache/tomcat8

Summary:    Boundless Server Apache Servlet/JSP Engine, RI for Servlet 3.1/JSP 2.3 API
Name:       boundless-server-tomcat8-manager
Version:    8.5.54
BuildArch:  noarch
Release:    1%{?dist}
License:    Apache Software License
Group:      Networking/Daemons
URL:        http://tomcat.apache.org/
Source0:    http://archive.apache.org/dist/tomcat/tomcat-8/v%{version}/bin/apache-tomcat-%{version}.tar.gz
Requires:   boundless-server-tomcat8
Obsoletes: suite-tomcat8-manager
Conflicts: suite-tomcat8-manager
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

This package contains the tomcat manager webapp.

%prep
%setup -q -n apache-tomcat-%{version}

%build

%install
# Add webapp
install -d -m 775 %{buildroot}%{tomcat_user_home}/webapps
mv webapps/manager/manager.war %{buildroot}%{tomcat_user_home}/webapps
chmod 775 %{buildroot}/%{tomcat_user_home}/webapps/*

%clean
rm -rf %{buildroot}

%pre
if [ -f /etc/init.d/tomcat8 ]; then
  /etc/init.d/tomcat8 stop > /dev/null 2>&1
fi

%files
%defattr(-,%{tomcat_user},%{tomcat_group})
%{tomcat_user_home}/webapps/*

%post

%preun
if [ $1 = 0 ]; then
  service tomcat8 stop > /dev/null 2>&1
fi

%postun

%changelog
