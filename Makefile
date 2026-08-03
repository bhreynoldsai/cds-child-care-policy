.PHONY: all docx pdf dashboard reference clean distclean

all: docx pdf dashboard

docx:
	python3 scripts/build.py --docx-only

pdf:
	python3 scripts/build.py --pdf-only

dashboard:
	python3 scripts/build_dashboard.py

reference:
	python3 scripts/make_reference_docx.py

clean:
	rm -rf .build

distclean: clean
	rm -f dist/* assets/reference.docx
