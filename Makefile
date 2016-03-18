.PHONY: all

all: sitemap.xml

sitemap.xml: sitemap.template parse_sitemap.py
	python3 parse_sitemap.py
