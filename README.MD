![SpinStack](https://socialify.git.ci/opott/SpinStack/image?font=Raleway&forks=1&issues=1&language=1&name=1&owner=1&pattern=Floating+Cogs&pulls=1&stargazers=1&theme=Dark)
A tool for managing a vinyl record collection created in Python with Airtable and the Discogs API.

[![asciicast](https://asciinema.org/a/LTYZtja9ISPxvpB2loNLKJ7sE.svg)](https://asciinema.org/a/LTYZtja9ISPxvpB2loNLKJ7sE)

## How to Use
1. Download the latest release from the [Releases](https://github.com/opott/SpinStack/releases) page.
2. Extract the `.zip` file.
3. Copy [this](https://airtable.com/appUljGOxFFwfawjh/shrJkKQ6eM7xT4nUj) Airtable base.
4. Open the `.env` file and fill the values:
    - `AIRTABLE_PAT`
        - Obtain a [Personal Access Token](https://airtable.com/create/tokens) from the Airtable Developer Hub.
    - `BASE_ID`
        - The part of the Airtable URL beginning with 'app'.
        - e.g. `appUljGOxFFwfawjh`
    - `TABLE_ID`
        - The part of the Airtable URL beginning with 'tbl'.
        - e.g. `tblmQM95rz4MKlqMP`
    - `DISCOGS_TOKEN`
        - Obtain a [Personal Access Token](https://www.discogs.com/settings/developers) from the Discogs Developer Hub.
5. Install dependencies:
    - `pip install -r requirements.txt`
6. Run `main.py`:
    - `python3 main.py`

## Contributing
I welcome all reasonable contributions! Please feel free to open a Pull Request.

## License
Licensed under the GNU General Public License 3.0.