#!/bin/bash
gunicorn -w 4 refreshPC:app -b 0.0.0.0:8080 -D --pid ./refreshPC.pid  --log-file ./log --error-logfile ./errlog
