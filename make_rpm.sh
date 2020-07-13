VERSION=$(grep "Version:" tomcat8.spec |cut -d ":" -f2 |tr -d "[:space:]")
RELEASE=$(grep "Release:" tomcat8.spec |cut -d ":" -f2 |tr -d "[:space:]")
ARCH=$(grep "BuildArch:" tomcat8.spec |cut -d ":" -f2 |tr -d "[:space:]")

echo "Version: $VERSION-$RELEASE BuildArch: $ARCH"

rm -rf rpmbuild
mkdir rpmbuild
mkdir rpmbuild/BUILD
mkdir rpmbuild/RPMS
mkdir rpmbuild/SOURCES
mkdir rpmbuild/SPECS
mkdir rpmbuild/SRPMS

wget http://archive.apache.org/dist/tomcat/tomcat-8/v$VERSION/bin/apache-tomcat-$VERSION.tar.gz -O apache-tomcat-$VERSION.tar.gz

##########################
# Add custom tomfoolery
# POC- Nick
##########################
tar -xzpf apache-tomcat-$VERSION.tar.gz
cp marlin/marlin*.jar apache-tomcat-$VERSION/lib
cp java-libs apache-tomcat-$VERSION/conf
mv apache-tomcat-$VERSION.tar.gz apache-tomcat-$VERSION.tar.gz.old
cd apache-tomcat-$VERSION/webapps/manager/
jar -cvf manager.war *
cd -
tar -czpf apache-tomcat-$VERSION.tar.gz apache-tomcat-$VERSION

ln -v -s "$(pwd)/apache-tomcat-$VERSION.tar.gz" "rpmbuild/SOURCES/"
ln -v -s "$(pwd)/tomcat8."{init,logrotate,sysconfig,bin,conf} "rpmbuild/SOURCES/"
ln -v -s "$(pwd)/tomcat8.spec" "rpmbuild/SPECS/"

cd rpmbuild

rpmbuild --buildroot "`pwd`/BUILDROOT" ../tomcat8.spec -bb --define "_topdir `pwd`"
rpmbuild --buildroot "`pwd`/BUILDROOT" ../tomcat8-manager.spec -bb --define "_topdir `pwd`"
