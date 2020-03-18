#include .env.project
#export # will export content of .env.project
all:  pip
.PHONY: all

SHELL := /usr/bin/env bash
MAKEFLAGS += --jobs=3


pip:
	pip install -r requirements.txt

CID:
	python3.7 main.py CID

prod:
	python3.7 main.py PROD

