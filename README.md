# S&P Data Fetcher
Fetches data about S&amp;P 500 companies and writes them to a CSV file. This was created for a Computer Science class project. Expect this to take around 30 minutes to complete with a free Finnhub account.

# Instruction
1. `git clone https://github.com/JackoCoolio/sandp-data-fetcher.git`
2. `pip install -r requirements.txt`
3. Edit `config.yaml`
4. `python app.py`

# Config
- `token`: Your [Finnhub](https://finnhub.io/) API key.
- `delay`: The number of milliseconds to wait between each company. Use this in order to not exceed Finnhub's API limit. Theoretically, with a free Finnhub account, this has to be set to >=3000ms.
- `outputFile`: The file to output the CSV data to.

## Example `config.yaml`
```YAML
token: g8sd7grw987hfg8bv7nj7
delay: 3000
outputFile: ./data.csv
```
