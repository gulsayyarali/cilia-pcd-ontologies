.PHONY: setup preprocess build validate reason query package all clean

PY ?= py

setup:
	$(PY) -m pip install -r requirements.txt

preprocess:
	$(PY) src/generate_synthetic_data.py
	$(PY) src/preprocess.py

build: preprocess
	$(PY) src/build_graph.py

validate: build
	$(PY) src/validate.py

reason: validate
	$(PY) src/reason.py

query: reason
	$(PY) src/query.py

package: query
	$(PY) src/package.py

all: package

clean:
	-$(PY) -c "import shutil, pathlib; \
p=pathlib.Path('.'); \
[shutil.rmtree(x, ignore_errors=True) for x in [p/'data', p/'rdf', p/'docs'/'query_results']]; \
print('cleaned local generated dirs')"
