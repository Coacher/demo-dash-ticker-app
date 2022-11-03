from fastapi import FastAPI, Path
from tickers import TradeSourceService


service = TradeSourceService()
app = FastAPI()

valid_index = Path(
    title='Ticker index',
    ge=min(service.sources.keys()),
    le=max(service.sources.keys()),
)


@app.on_event('startup')
def startup():
    service.start()


@app.on_event('shutdown')
def shutdown():
    service.stop()


@app.get('/tickers')
def get_tickers():
    return {'tickers': service.get_indices()}


@app.get('/tickers/names')
def get_tickers_names():
    return {'tickers_names': service.get_names()}


@app.get('/tickers/names/{name}')
def get_ticker_index(name: str):
    try:
        return {'index': service.get_index(name)}
    except ValueError:
        return {'message': 'Incorrect trade source name'}


@app.get('/tickers/{index}')
def get_ticker_name(index: int = valid_index):
    return {'name': service.get_name(index)}


@app.get('/tickers/{index}/price')
def get_ticker_price(index: int = valid_index):
    return {'price': service.get_price(index)}


@app.get('/tickers/{index}/point')
def get_ticker_point(index: int = valid_index):
    return {'point': service.get_point(index)}


@app.get('/tickers/{index}/history')
def get_ticker_history(index: int = valid_index):
    return {'history': service.get_history(index)}
