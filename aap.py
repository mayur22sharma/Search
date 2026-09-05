"""
Sherlock username lookup — Streamlit front-end.

Wraps the `sherlock-project` CLI so you can run username searches
from a web UI, deployed via Streamlit Community Cloud (streamlit.app).
"""

import subprocess
import sys
import tempfile
import os
import time

import streamlit as st

st.set_page_config(page_title="Sherlock Username Lookup", page_icon="🔎")

st.title("🔎 Sherlock Username Lookup")
st.caption(
    "Checks a username against hundreds of sites using the "
    "[Sherlock Project](https://sherlockproject.xyz/) OSINT tool."
)

with st.form("lookup_form"):
    username = st.text_input("Username to search", placeholder="e.g. octocat")
    col1, col2 = st.columns(2)
    with col1:
        timeout = st.slider("Per-site timeout (seconds)", 5, 60, 20)
    with col2:
        include_nsfw = st.checkbox("Include NSFW-flagged sites", value=False)
    submitted = st.form_submit_button("Search")

if submitted:
    if not username.strip():
        st.warning("Enter a username first.")
        st.stop()

    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, f"{username}.txt")

        cmd = [
            sys.executable, "-m", "sherlock_project",
            username.strip(),
            "--timeout", str(timeout),
            "--print-found",   # only show hits, keeps output readable
            "--folderoutput", tmpdir,
        ]
        if include_nsfw:
            cmd.append("--nsfw")

        status = st.empty()
        log_box = st.empty()
        status.info(f"Searching for `{username}` across sites… this can take a minute or two.")

        start = time.time()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # hard cap so the app can't hang forever
            )
        except subprocess.TimeoutExpired:
            status.error("Search timed out after 10 minutes. Try a shorter per-site timeout.")
            st.stop()

        elapsed = time.time() - start
        status.success(f"Done in {elapsed:.1f}s")

        if proc.stdout:
            with st.expander("Raw output", expanded=True):
                st.code(proc.stdout, language="text")

        if proc.returncode != 0 and proc.stderr:
            with st.expander("Errors / warnings"):
                st.code(proc.stderr, language="text")

        # Sherlock writes results to <folder>/<username>.txt
        if os.path.exists(out_file):
            with open(out_file, "r", encoding="utf-8") as f:
                results = f.read()
            st.subheader("Found accounts")
            st.text_area("Results", results, height=300)
            st.download_button(
                "Download results (.txt)",
                data=results,
                file_name=f"{username}_sherlock_results.txt",
                mime="text/plain",
            )
        else:
            st.info("No results file was produced — check the raw output above.")

st.divider()
st.caption(
    "Note: this runs the real Sherlock scan on the server, which can take a while "
    "for 400+ sites and may hit rate limits on Streamlit Community Cloud's shared "
    "infrastructure. Consider narrowing sites with `--site` if you fork this."
)
