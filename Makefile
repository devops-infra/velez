.PHONY: clean install install-dev reinstall test

clean:
	@rm -rf dist build *.egg-info

install: clean
	@python3 -m build --wheel
	@pip3 install dist/*.whl

install-dev: clean
	@pip3 install -r requirements.txt

reinstall: clean
	@python3 -m build --wheel
	@pip3 install dist/*.whl --force-reinstall

test:
	@pytest -v --tb=short
