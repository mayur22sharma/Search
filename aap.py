import subprocess
import sys
import tempfile
import os
import streamlit as st

st.set_page_config(
    page_title="Sherlock Streamlit App",
    page_icon="🔍",
    layout="centered"
)

st.title("🔍 Sherlock Username Checker")
st.write("Enter a username to search across hundreds of social media platforms.")

# Input form
with st.form("sherlock_form"):
    username = st.text_input("Username to search:", placeholder="e.g., johndoe")
    submit_button = st.form_submit_button(label="Run Search")

if submit_button:
    if not username.strip():
        st.warning("Please enter a valid username.")
    else:
        st.info(f"Searching for **{username}** across platforms... Please wait.")
        
        # Use a temporary directory to store Sherlock's output file
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_file = os.path.join(tmpdirname, f"{username}.txt")
            
            # Construct the command line arguments for sherlock
            # --print-found prints only found accounts, --output saves results
            cmd = [
                sys.executable, "-m", "sherlock",
                username,
                "--print-found",
                "--output", output_file
            ]
            
            try:
                # Run the subprocess and capture output
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=120  # Timeout after 2 minutes to prevent hanging
                )
                
                # Display standard output or read the generated file
                if os.path.exists(output_file):
                    with open(output_file, "r", encoding="utf-8") as f:
                        results = f.read()
                    
                    if results.strip():
                        st.success("Search complete!")
                        st.text_area("Results Log:", results, height=300)
                        
                        # Provide download button for the text report
                        st.download_button(
                            label="Download Results (TXT)",
                            data=results,
                            file_name=f"sherlock_{username}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.warning("No accounts found or the search returned empty results.")
                else:
                    st.error("Sherlock executed, but no output file was generated.")
                    if process.stderr:
                        st.code(process.stderr)
                        
            except subprocess.TimeoutExpired:
                st.error("The search took too long and timed out.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
