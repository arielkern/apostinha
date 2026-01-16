import json
import os
import yfinance as yf
from datetime import datetime
import pandas as pd

START_DATE = '2024-12-13'
CONTEST_END_DATE = '2025-12-13'

TICKERS = {
    'Ari': ['BBAS3', 'VALE3', 'EQTL3'],
    'Vai': ['MDIA3', 'NATU3', 'FLRY3'],  # mantém o lógico "NATU3"
    'Jai': ['ITUB4', 'LREN3', 'SUZB3'],
    'IBOV': ['^BVSP']
}

# Data de corte para NATU3 (a partir daqui baixa NATU3 do Yahoo)
NATU3_CUTOFF = '2025-07-02'

# Saída
BUCKET_NAME = 'teleturfe-website-prod'
OBJECT_KEY = 'portfolios.json'

# Caminho do natu3.json empacotado com a Lambda
# (/var/task é o diretório do código em tempo de execução)
NATU3_JSON_BUNDLED_PATH = os.path.join(os.path.dirname(__file__), 'natu3.json')


def _ensure_datetime_index_sorted(df: pd.DataFrame) -> pd.DataFrame:
    df.index = pd.to_datetime(df.index, errors='coerce')
    df = df[~df.index.isna()]
    df.sort_index(inplace=True)
    return df


def _load_natu3_json_from_bundle() -> dict | None:
    """Carrega natu3.json do próprio bundle da Lambda (sem S3)."""
    try:
        with open(NATU3_JSON_BUNDLED_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def _parse_natu3_series_from_json(payload: dict) -> pd.Series:
    """
    Constrói uma pd.Series (index datetime, valores float) a partir do json.
    Aceita formatos:
      {"dates":[...], "prices":[...]}  (ou "values"/"closes"/"series")
    ou um array simples numérico (mas aí precisa do campo "dates").
    Retorna Series possivelmente vazia se não conseguir parsear.
    """
    if payload is None:
        return pd.Series(dtype='float64')

    # Tenta extrair datas
    dates = None
    if isinstance(payload, dict) and 'dates' in payload and isinstance(payload['dates'], list):
        dates = payload['dates']

    # Tenta extrair preços
    candidates = ['prices', 'values', 'closes', 'series']
    prices = None
    if isinstance(payload, dict):
        for k in candidates:
            if k in payload and isinstance(payload[k], list):
                prices = payload[k]
                break
        # Caso tenha uma chave "data" com lista
        if prices is None and isinstance(payload.get('data'), list):
            prices = payload['data']

    # Caso o arquivo seja APENAS um array (sem chaves)
    if prices is None and isinstance(payload, list):
        prices = payload

    if dates is None or prices is None:
        return pd.Series(dtype='float64')

    if len(dates) != len(prices):
        n = min(len(dates), len(prices))
        dates = dates[:n]
        prices = prices[:n]

    try:
        idx = pd.to_datetime(dates, errors='coerce')
        s = pd.to_numeric(pd.Series(prices, index=idx),
                          errors='coerce').dropna()
        s.index = pd.to_datetime(s.index)
        s = s.sort_index()
        return s
    except Exception:
        return pd.Series(dtype='float64')


def _merge_natu3_json_pre_cutoff(close_df: pd.DataFrame) -> pd.DataFrame:
    """
    Lê natu3.json empacotado e injeta os valores APENAS para datas < NATU3_CUTOFF na coluna 'NATU3.SA'.
    A partir do cutoff, mantém o que vier do Yahoo. Se não houver coluna NATU3.SA ainda,
    cria a coluna com base no índice do DataFrame.
    """
    payload = _load_natu3_json_from_bundle()
    s_json = _parse_natu3_series_from_json(payload)
    if s_json.empty:
        return close_df

    cutoff = pd.to_datetime(NATU3_CUTOFF)

    # Apenas o trecho anterior ao cutoff
    pre_cut = s_json.loc[s_json.index < cutoff]
    if pre_cut.empty:
        return close_df

    # Garante índice ordenado no df principal
    close_df = _ensure_datetime_index_sorted(close_df)

    # Garante existência da coluna NATU3.SA
    if 'NATU3.SA' not in close_df.columns:
        close_df['NATU3.SA'] = pd.NA

    # Garante que todas as datas do pre_cut estão presentes no índice do DF
    new_index = sorted(set(close_df.index.union(pre_cut.index)))
    close_df = close_df.reindex(new_index)

    # Sobrescreve valores < cutoff com os do JSON (preço ajustado esperado)
    close_df.loc[pre_cut.index, 'NATU3.SA'] = pre_cut.astype(float).values

    return close_df


def lambda_handler(event, context):
    # Universo lógico (sem .SA) para os portfólios + IBOV
    tickers = TICKERS['Ari'] + TICKERS['Jai'] + TICKERS['Vai']

    # Converte para Yahoo (.SA), exceto IBOV
    tickers_b3 = [ticker.upper() + ".SA" for ticker in tickers] + \
        TICKERS['IBOV']

    # Download histórico (ajustado) – já inclui NATU3.SA (pós-corte)
    data = yf.download(sorted(set(tickers_b3)),
                       start=START_DATE, interval='1d', auto_adjust=True)

    # Extrai/normaliza DataFrame de Close
    if isinstance(data, pd.DataFrame) and 'Close' in data.columns:
        close_df = data['Close'].copy()
    else:
        close_df = data.copy()
        if isinstance(close_df, pd.Series):
            close_df = close_df.to_frame()
        try:
            close_df = data['Close'].copy()
        except Exception:
            pass

    close_df = _ensure_datetime_index_sorted(close_df)

    # Injeta histórico pré-corte da Natura a partir do natu3.json (bundle)
    close_df = _merge_natu3_json_pre_cutoff(close_df)

    # Injeta intraday (1m) diretamente nas colunas finais — preserva retorno intraday no front
    today_dt = pd.Timestamp.today().normalize()
    for ticker in sorted(set(tickers_b3)):
        try:
            h = yf.Ticker(ticker).history(
                period="1d", interval="1m", auto_adjust=True)
            if h.empty or 'Close' not in h.columns:
                h = yf.Ticker(ticker).history(period="1d", auto_adjust=True)
            if not h.empty and 'Close' in h.columns:
                last_px = float(h['Close'].dropna().iloc[-1])
                # atualiza linha do dia
                close_df.loc[today_dt, ticker] = last_px
        except Exception:
            # Erros transitórios do Yahoo: ignora
            pass

    close_df = _ensure_datetime_index_sorted(close_df)

    contest_end = pd.to_datetime(CONTEST_END_DATE)
    close_df = close_df.loc[close_df.index <= contest_end]

    # Pipeline original
    data = close_df  # 'data' é Close já tratado
    sorted_dates = [d.strftime('%Y-%m-%d') for d in data.index.unique()]

    output = {
        "updatedAt": datetime.now().isoformat(),
        "data": {
            "dates": sorted_dates,
            "portfolios": {}
        }
    }

    for portfolio_name, ticker_list in TICKERS.items():
        portfolio_tickers_b3 = ticker_list if portfolio_name == 'IBOV' else [
            t.upper() + ".SA" for t in ticker_list]
        sub_data = data[portfolio_tickers_b3].copy()

        sub_data.ffill(inplace=True)

        inception_prices = sub_data.iloc[0].copy()

        assets_dict = {t: [] for t in ticker_list}         # ITD por papel
        assets_prices_dict = {t: []
                              for t in ticker_list}  # preço bruto por papel
        portfolio_return_list = []

        # Itera por data em ordem
        for date in sub_data.index:
            current_prices = sub_data.loc[date]
            itd_values = []

            for tkr in ticker_list:
                tkr_b3 = tkr if portfolio_name == 'IBOV' else tkr.upper() + ".SA"

                price = current_prices[tkr_b3]
                if isinstance(price, pd.Series):
                    price = price.iloc[-1]
                assets_prices_dict[tkr].append(
                    None if pd.isna(price) else float(price))

                itd_price = inception_prices[tkr_b3]
                if isinstance(itd_price, pd.Series):
                    itd_price = itd_price.iloc[-1]

                if pd.isna(itd_price) or itd_price == 0:
                    itd = float('nan')
                else:
                    itd = (price / itd_price -
                           1) if pd.notna(price) else float('nan')

                assets_dict[tkr].append(None if pd.isna(itd) else float(itd))
                itd_values.append(itd)

            valid_vals = [v for v in itd_values if not pd.isna(v)]
            portfolio_itd = sum(valid_vals) / \
                len(valid_vals) if valid_vals else float('nan')
            portfolio_return_list.append(None if pd.isna(
                portfolio_itd) else float(portfolio_itd))

        output["data"]["portfolios"][portfolio_name] = {
            "assets": assets_dict,
            "assetPrices": assets_prices_dict,
            "portfolioReturn": portfolio_return_list
        }

    json_body = json.dumps(output)

    # Grava no S3 (a Lambda só lê o JSON do bundle; a saída continua no S3)
    import boto3
    s3_client = boto3.client('s3')
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=OBJECT_KEY,
        Body=json_body,
        ContentType='application/json'
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "ok"})
    }


if __name__ == '__main__':
    lambda_handler('', '')
