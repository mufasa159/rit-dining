### RIT Dining - Web Scraper for Visiting Chefs

A simple starlette program for scrapping RIT Dining webpage for visiting chefs on campus. Made it so that the UI is clean and without distraction.


### Local Setup

```
python3 -m venv .venv
```
```
source .venv/bin/activate  // macos
.venv\Scripts\activate     // windows
```
```
pip3 install -r requirements.txt
```

Run the project using:
```
uvicorn main:app --reload
```