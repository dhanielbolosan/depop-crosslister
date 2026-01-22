<h1>Command Line Powered Script to download posts from depop</h1>

<h3>Setting Up Virtual Environment</h3>
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install

<h3>Running the Script<h3>
python download_from_depop.py