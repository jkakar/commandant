all:
	@test -n "$$VIRTUAL_ENV" || { echo "You're not in a virtualenv.  Create one by running: virtualenv .; . bin/activate"; exit 1; }
	pip install -r requirements.txt --upgrade

clean:
	find . -name \*pyc -exec rm {} \;
	rm -rf _trial_temp

check:
	@trial commandant

pyflakes:
	@pyflakes commandant

pep8:
	@find commandant \
	    -name '*.py' ! -path 'commandant/testing/mocker.py' \
	    -print0 | xargs -r0 pep8

lint: pep8 pyflakes

doc:
	@pydoctor \
		--project-name Commandant \
		--project-url "https://github.com/jkakar/commandant" \
		--project-base-dir `pwd` \
		--add-package commandant \
		--make-html

info:
	@echo "Revision:"
	@bzr revno
	@echo
	@echo "Lines of application code:"
	@find commandant -name \*py | grep -v test_ | grep -v mocker | \
		xargs cat | wc -l
	@echo
	@echo "Lines of test code:"
	@find commandant -name \*py | grep test_ | xargs cat | wc -l

login:
	@python setup.py sdist register

publish:
	@python setup.py sdist upload

release:
	@python setup.py sdist
