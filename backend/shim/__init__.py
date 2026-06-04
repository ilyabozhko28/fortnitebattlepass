"""Thin FastAPI transport for the harmony script package.

Its single job is to let a browser call ``harmony.pipeline.run`` over HTTP.
No DB, no auth, no sessions, no logging of pixel data.
"""
