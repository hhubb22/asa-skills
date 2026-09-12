PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: sync check test release
sync:
	$(PYTHON) tools/sync_shared.py
check:
	$(PYTHON) tools/check.py
test:
	$(PYTHON) -m unittest discover -s tests -v
release: check test
	$(PYTHON) tools/build_release.py
