NAME    = saternet
VERSION = 1.0.0
ARCH    = all
PKG     = $(NAME)_$(VERSION)_$(ARCH)

.PHONY: deb pkgbuild install clean

deb:
	mkdir -p dist/$(PKG)/DEBIAN
	mkdir -p dist/$(PKG)/usr/local/bin
	mkdir -p dist/$(PKG)/usr/local/lib/saternet
	mkdir -p dist/$(PKG)/usr/share/pixmaps
	mkdir -p dist/$(PKG)/usr/share/applications

	cp debian/control dist/$(PKG)/DEBIAN/control
	cp debian/postinst dist/$(PKG)/DEBIAN/postinst
	chmod 755 dist/$(PKG)/DEBIAN/postinst

	cp src/saternet.py dist/$(PKG)/usr/local/lib/saternet/saternet.py

	echo '#!/usr/bin/env bash' > dist/$(PKG)/usr/local/bin/saternet
	echo 'exec python3 /usr/local/lib/saternet/saternet.py "$$@"' >> dist/$(PKG)/usr/local/bin/saternet
	chmod 755 dist/$(PKG)/usr/local/bin/saternet

	cp assets/saternet.png dist/$(PKG)/usr/share/pixmaps/saternet.png 2>/dev/null || true
	cp assets/saternet.desktop dist/$(PKG)/usr/share/applications/saternet.desktop

	dpkg-deb --build dist/$(PKG)
	mv dist/$(PKG).deb dist/$(NAME)_$(VERSION).deb
	@echo
	@echo "  built  dist/$(NAME)_$(VERSION).deb"
	@echo "  install with:  sudo dpkg -i dist/$(NAME)_$(VERSION).deb"
	@echo

install:
	bash install.sh

clean:
	rm -rf dist/
