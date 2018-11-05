PYTHON = python2
UP2DATE = $(shell grep --silent `$(PYTHON) ./setup.py --version` debian/changelog &> /dev/null ; echo $$?)

.PHONY: up2date
ifneq ($(UP2DATE),0)
up2date:
  $(error "Update your Version strings/Changelogs")
else
up2date:
  $(info "Version strings/Changelogs up to date")
endif

release:
	$(PYTHON) setup.py sdist
	@echo && echo "Did you run distclean?"

debrelease: up2date
	echo 'recursive-include debian *' >> MANIFEST.in
	dh_clean
	make release
	git checkout MANIFEST.in

deb:
	[ -d ./debian ] || (echo "Your checkout/tarball does not contain a debian directory" && false)
	debuild -i -us -uc -b

rpm:
	$(PYTHON) setup.py bdist_rpm
