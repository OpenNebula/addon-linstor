PYTHON = python2

release:
	$(PYTHON) setup.py sdist
	@echo && echo "Did you run distclean?"

debrelease:
	echo 'recursive-include debian *' >> MANIFEST.in
	dh_clean
	make release
	git checkout MANIFEST.in

deb:
	[ -d ./debian ] || (echo "Your checkout/tarball does not contain a debian directory" && false)
	debuild -i -us -uc -b

rpm:
	$(PYTHON) setup.py bdist_rpm
