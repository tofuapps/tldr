# News Reader

A system which can
* automatically curate topics/articles from multiple news sources online, and
* summarise topics’ contents.

Features include:
* Summarizing single articles
* Summarizing groups of articles on the same topic
* Summarizing articles related to a query

App structure, powered by:
* UI/Web Server
    + Vue.js
    + Node.js
* API Server
    + Flask
* AI Backend
    + feedparser
    + newspaper3k
    + Beautiful Soup
    + scikit-learn
    + nltk

## Installing & Setup
You will need the following on your system:

* Python3
* Pip3
* Pipenv

Once you're done, install the dependencies of the project by entering the following while in the root directory of the project:
```
pipenv sync
```

Additionally, you need to download some corpora from `nltk`.
To do so, run the following in a python shell.
```
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
```

Install nodejs dependencies by running the following in the `ui` subdirectory.
```
npm install
```

## Running

You will need to start both the UI and API server. A script `tmux.sh` is available to start both servers in split view in a detached tmux session, which can be used on macOS and Linux systems with `tmux` installed.

If you do not have `tmux`, follow the below steps to manually start the servers.

### UI Server
Start a new shell in the current directory, navigate to the `ui` subdirectory and enter
```
npm start
```

### API Server
Now, in a separate shell in the current directory, enter
```
pipenv run python3 api_server.py
```
Configuration:
- Create a file `useCachedFeed` in the same directory as `api_server.py` to force the api server to always use the cached feed.

### Command-line Interface
If you only want to test the AI component of this project, run
```
pipenv run python3 main.py
```
An empty output is expected. Pass the option `--help` or `-h` to view the complete list of available options.

## Usage

To use the News Reader, go to `http://localhost:8080` on your system. This web app is tested to function on Chrome, Firefox, and Safari.

As of now, the default feed includes contents from Channel News Asia, BBC and The Straits Times.

## Contributors
- Li Yue Chen (@l-yc)
- Lim Wern Jie (@wernjie)
