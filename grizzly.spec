%global namedreltag %{nil}
%global _version %(echo %version | tr . _)
%global namedversion %{_version}%{?namedreltag}
%bcond_with jersey
%bcond_with jaxws
Name:                grizzly
Version:             2.3.24
Release:             2
Summary:             Java NIO Server Framework
License:             (CDDL or GPLv2 with exceptions) and BSD and ASL 2.0 and Public Domain
URL:                 http://grizzly.java.net/
Source0:             https://github.com/javaee/grizzly/archive/2_3_24.tar.gz
BuildRequires:       maven-local mvn(com.sun.istack:istack-commons-maven-plugin)
%if %{with jersey}
BuildRequires:       mvn(com.sun.jersey:jersey-client) mvn(com.sun.jersey:jersey-server)
BuildRequires:       mvn(com.sun.jersey:jersey-servlet)
%endif
%if %{with jaxws}
BuildRequires:       mvn(com.sun.xml.ws:rt)
%endif
BuildRequires:       mvn(javax.servlet:javax.servlet-api) mvn(junit:junit)
BuildRequires:       mvn(net.java:jvnet-parent:pom:) mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:       mvn(org.apache.maven.plugins:maven-enforcer-plugin)
BuildRequires:       mvn(org.codehaus.mojo:build-helper-maven-plugin)
BuildRequires:       mvn(org.codehaus.mojo:exec-maven-plugin) mvn(org.glassfish.gmbal:gmbal)
BuildRequires:       mvn(org.glassfish.gmbal:gmbal-api-only)
BuildRequires:       mvn(org.glassfish.grizzly:grizzly-npn-api)
BuildRequires:       mvn(org.glassfish.grizzly:grizzly-npn-bootstrap)
BuildRequires:       mvn(org.glassfish.hk2:hk2-inhabitant-generator)
BuildRequires:       mvn(org.glassfish.hk2:osgiversion-maven-plugin) mvn(org.mockito:mockito-all)
BuildRequires:       mvn(org.osgi:org.osgi.compendium) mvn(org.osgi:org.osgi.core)
BuildArch:           noarch
%description
Writing scalable server applications in the Java programming
language has always been difficult. Before the advent of the
Java New I/O API (NIO), thread management issues made it
impossible for a server to scale to thousands of users. The
Grizzly framework has been designed to help developers to take
advantage of the Java NIO API. Originally developed under the
GlassFish umbrella, the framework is now available as a
standalone project. Grizzly goals is to help developers to
build scalable and robust servers using NIO.

%package samples
Summary:             Grizzly samples
%description samples
This package contains samples for %{name}.

%package javadoc
Summary:             Javadoc for %{name}
%description javadoc
This package contains javadoc for %{name}.

%prep
%setup -q -n %{name}-mirror-%{namedversion}
find . -name '*.class' -delete
find . -name '*.jar' -print -delete
find . -name '*.js' -print -delete
%pom_disable_module bundles extras
%pom_disable_module bundles modules
%pom_disable_module grizzly-httpservice extras
%pom_disable_module comet samples
%pom_disable_module websockets/chat samples
%pom_disable_module websockets/chat-ssl samples
%pom_remove_dep :maven-bundle-plugin
%pom_remove_dep :maven-plugin-tools-api
%pom_remove_dep org.glassfish.hk2:config-types
%pom_remove_dep org.glassfish.hk2:core
%pom_remove_dep org.glassfish.hk2:hk2-config
%pom_remove_dep org.glassfish.hk2:hk2-locator
%pom_remove_dep org.glassfish.hk2:osgi-adapter
%pom_xpath_remove "pom:build/pom:extensions"
%pom_xpath_inject "pom:dependency[pom:artifactId = 'grizzly-spdy']" '<version>${project.version}</version>' samples/spdy-samples
%pom_remove_dep org.glassfish.grizzly:grizzly-comet-server bom
%pom_remove_dep org.glassfish.grizzly:grizzly-compression bom
%pom_remove_dep org.glassfish.grizzly:grizzly-core bom
%pom_remove_dep org.glassfish.grizzly:grizzly-http-all bom
%pom_remove_dep org.glassfish.grizzly:grizzly-http-server-core bom
%pom_remove_dep org.glassfish.grizzly:grizzly-http-server-jaxws bom
%pom_remove_dep org.glassfish.grizzly:grizzly-http-servlet-server bom
%pom_remove_dep org.glassfish.grizzly:grizzly-websockets-server bom
%pom_remove_dep org.glassfish.grizzly.osgi:grizzly-httpservice bom
%pom_remove_dep org.glassfish.grizzly.osgi:grizzly-httpservice-bundle bom
%pom_remove_plugin :maven-antrun-extended-plugin bom
%pom_remove_plugin :glassfish-copyright-maven-plugin bom
%pom_remove_plugin :findbugs-maven-plugin
%pom_remove_plugin :glassfish-copyright-maven-plugin
%pom_remove_plugin :nexus-maven-plugin
%pom_remove_plugin :maven-source-plugin
%pom_xpath_remove "pom:plugin[pom:artifactId='maven-javadoc-plugin']/pom:executions"
%if %{without jersey}
%pom_remove_dep com.sun.jersey: modules/http-servlet
rm -rf modules/http-servlet/src/test/java/filter/*
%else
%pom_add_dep com.sun.jersey:jersey-servlet:'${jersey-version}':test modules/http-servlet
%endif
cp -p modules/grizzly/src/main/resources/Grizzly_THIRDPARTYLICENSEREADME.txt .
sed -i 's/\r//' LICENSE.txt Grizzly_THIRDPARTYLICENSEREADME.txt
%pom_xpath_set -r "pom:plugin[pom:groupId='com.sun.istack']/pom:artifactId" istack-commons-maven-plugin
%pom_change_dep -r javax.servlet:servlet-api javax.servlet:javax.servlet-api:'${servlet-version}'
%if %{without jaxws}
%pom_disable_module http-server-jaxws extras
%pom_disable_module http-jaxws-samples samples
%else
%pom_change_dep com.sun.xml.ws: :rt extras/http-server-jaxws
%pom_change_dep com.sun.xml.ws: :rt samples/http-jaxws-samples
%endif
for m in http2 spdy ; do
%pom_xpath_remove "pom:plugin[pom:artifactId='maven-jar-plugin']/pom:configuration/pom:useDefaultManifestFile" modules/${m}
%pom_xpath_inject "pom:plugin[pom:artifactId='maven-jar-plugin']/pom:configuration" '
  <archive>
    <manifestFile>${project.build.outputDirectory}/META-INF/MANIFEST.MF</manifestFile>
  </archive>' modules/${m}
done
%mvn_package org.glassfish.grizzly.samples: samples
# remove <scope>test</scope>
%pom_xpath_remove "pom:dependency[pom:artifactId='junit']/pom:scope"
%pom_xpath_remove "pom:dependency[pom:artifactId='mockito-all']/pom:scope" modules/http-server

%build
%mvn_build \
%ifarch %{arm}
 -f -- \
%else
 --skipTests -- \
%endif
 -Dmaven.local.depmap.file="%{_mavendepmapfragdir}/glassfish-servlet-api.xml"

%install
%mvn_install
(
  cd %{buildroot}%{_javadir}/%{name}
  ln -sf %{name}-framework.jar %{name}.jar
)

%check
%ifnarch %{arm}
xmvn test --batch-mode --offline verify -Dmaven.test.failure.ignore=true
%endif

%files -f .mfiles
%{_javadir}/%{name}/%{name}.jar
%license LICENSE.txt Grizzly_THIRDPARTYLICENSEREADME.txt

%files samples -f .mfiles-samples
%license LICENSE.txt Grizzly_THIRDPARTYLICENSEREADME.txt

%files javadoc -f .mfiles-javadoc
%license LICENSE.txt Grizzly_THIRDPARTYLICENSEREADME.txt

%changelog
* Tue Apr 27 2021 maminjie <maminjie1@huawei.com> - 2.3.24-2
- Move the test to the %check stage

* Fri Aug 28 2020 Anan Fu <fuanan3@huawei.com> - 2.3.24-1
- package init
