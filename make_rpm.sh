#!/bin/bash

set -e

VERSION=$(grep "Version:" tomcat8.spec |cut -d ":" -f2 |tr -d "[:space:]")
RELEASE=$(grep "Release:" tomcat8.spec |cut -d ":" -f2 |tr -d "[:space:]")
ARCH=$(grep "BuildArch:" tomcat8.spec |cut -d ":" -f2 |tr -d "[:space:]")

echo "Version: $VERSION-$RELEASE BuildArch: $ARCH"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RPMBUILD="${DIR}/build"

rm -rf ${RPMBUILD}/BUILD
rm -rf ${RPMBUILD}/SRPMS
rm -rf ${RPMBUILD}/RPMS
rm -f apache-tomcat-$VERSION.tar.gz apache-tomcat-$VERSION.tar.gz.old

wget http://archive.apache.org/dist/tomcat/tomcat-8/v$VERSION/bin/apache-tomcat-$VERSION.tar.gz -O apache-tomcat-$VERSION.tar.gz

tar -xzpf apache-tomcat-$VERSION.tar.gz

mv apache-tomcat-$VERSION.tar.gz apache-tomcat-$VERSION.tar.gz.old
cd apache-tomcat-$VERSION/webapps/manager/
jar -cvf manager.war *
cd -
tar -czpf apache-tomcat-$VERSION.tar.gz apache-tomcat-$VERSION
rm -rf apache-tomcat-$VERSION

RPM_OPTS=("-bb"
  "--define" "_topdir ${RPMBUILD}"
  "--define" "_sourcedir ${DIR}"
  "--define" "_buildrootdir %{_tmppath}"
  "--target" "${ARCH}"
)

rpmbuild tomcat8.spec "${RPM_OPTS[@]}"
rpmbuild tomcat8-manager.spec "${RPM_OPTS[@]}"
