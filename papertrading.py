import marimo

__generated_with = "0.11.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    return (pd,)


@app.cell
def _():
    # Model for Trade

    from typing import Optional
    from datetime import date


    from sqlmodel import Field, SQLModel


    # Define your models
    class Trade(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        symbol: str
        trade_date: date
        trade_type: int  # 1 = Long or -1 = Short
        last_close: Optional[float]
        atr30:  Optional[float]
        quantity:  Optional[int]
        open: Optional[float]
        close: Optional[float]
        profit: Optional[float]
        profit_original: Optional[float]
        gap_in_atr: Optional[float]
        limit_touched: Optional[bool]
        limit: Optional[float]
        notes: Optional[str] = None
    return Field, Optional, SQLModel, Trade, date


@app.cell
def _(SQLModel):
    from sqlmodel import create_engine
    import os
    DATABASE_URL = "sqlite:///papertrading.db"
    engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine)
    return DATABASE_URL, create_engine, engine, os


@app.cell
def _(Trade, date, engine):
    # Repository
    from sqlmodel import Session, select, delete
    from typing import List

    def add_trade(symbol: str, trade_date: date, trade_type: int):
        with Session(engine) as session:
            # Check if a trade with the same symbol and date exists
            statement = select(Trade).where(Trade.symbol == symbol, Trade.trade_date == trade_date)
            existing_trade = session.exec(statement).first()

            if existing_trade:
                # Update the existing trade
                existing_trade.trade_type = trade_type
            else:
                # Create a new trade if none exists
                existing_trade = Trade(
                    symbol=symbol,
                    trade_date=trade_date,
                    trade_type=trade_type,
                )
                session.add(existing_trade)

            # Commit changes
            session.commit()
            session.refresh(existing_trade)

            return existing_trade

    def update_atr(symbol: str, trade_date: date, atr30: float, last_close: float):
        with Session(engine) as session:
            # Check if a trade with the same symbol and date exists
            statement = select(Trade).where(Trade.symbol == symbol, Trade.trade_date == trade_date)
            existing_trade = session.exec(statement).first()

            if existing_trade:
                # Update the existing trade
                existing_trade.atr30 = atr30
                existing_trade.last_close = last_close
                existing_trade.quantity = int(1000 / atr30)
                existing_trade.limit = last_close + (existing_trade.trade_type * 0.4 * atr30)

            else:
                return None

            # Commit changes
            session.commit()
            session.refresh(existing_trade)

            return existing_trade

    def update_profit(symbol: str, trade_date: date, open_price: float, close_price: float):
        with Session(engine) as session:
            # Check if a trade with the same symbol and date exists
            statement = select(Trade).where(Trade.symbol == symbol, Trade.trade_date == trade_date)
            existing_trade = session.exec(statement).first()

            if existing_trade:
                # Update the existing trade
                existing_trade.open = open_price
                existing_trade.close = close_price
                gap = (open_price - existing_trade.last_close) * existing_trade.trade_type
                gap_in_atr = gap / existing_trade.atr30
                existing_trade.gap_in_atr = gap_in_atr
                profit = (close_price - open_price) * existing_trade.trade_type * existing_trade.quantity
                if gap_in_atr < 0.4:
                    existing_trade.profit = profit
                else:
                     existing_trade.profit = 0
                existing_trade.profit_original = profit


            else:
                return None

            # Commit changes
            session.commit()
            session.refresh(existing_trade)

            return existing_trade

    def get_trades_by_symbol(symbol: str) -> List[Trade]:
        with Session(engine) as session:
            statement = select(Trade).where(Trade.symbol == symbol)
            trades = session.exec(statement).all()
            return trades

    def get_trades_by_date(date: date) -> List[Trade]:
        with Session(engine) as session:
            statement = select(Trade).where(Trade.trade_date == date)
            trades = session.exec(statement).all()
            return trades

    def get_all_trades(date: date) -> List[Trade]:
        with Session(engine) as session:
            statement = select(Trade).order_by(Trade.trade_date)
            trades = session.exec(statement).all()
            return trades

    # Delete all trades from the database
    def delete_all_trades():
        with Session(engine) as session:
            # Create a delete statement for the Trade table
            statement = delete(Trade)
            result = session.exec(statement)
            session.commit()

            # Return the number of deleted rows
            return result.rowcount
    return (
        List,
        Session,
        add_trade,
        delete,
        delete_all_trades,
        get_all_trades,
        get_trades_by_date,
        get_trades_by_symbol,
        select,
        update_atr,
        update_profit,
    )


@app.cell
def _():
    import marimo as mo

    form1 = (
        mo.md('''
        ## Trading Database Management"

        {date_picker}

        {long_symbols}

        {short_symbols}
    ''')
        .batch(
            long_symbols = mo.ui.text(placeholder="long symbols, comma-separated", full_width=True ),
            short_symbols = mo.ui.text(placeholder="short symbols, comma-separated", full_width=True ),
            date_picker = mo.ui.date(label="Trade Date")
        )
        .form(show_clear_button=True)
    )
    form1
    return form1, mo


@app.cell
def _():
    from stock_download import download_stock_data, load_stock_data
    from indicators import calculate_atr
    return calculate_atr, download_stock_data, load_stock_data


@app.cell
def _(add_trade, calculate_atr, download_stock_data, form1, mo, update_atr):
    mo.stop(form1.value == None)
    vdate = form1.value["date_picker"]
    vlong = form1.value["long_symbols"] 
    vshort = form1.value["short_symbols"] 
    symbols = []
    c = 0
    # Process long positions
    for sym in vlong.split(','):
        if sym.strip() == '':
            continue
        # Call your add_trade function
        add_trade(symbol=sym.strip(), trade_date=vdate, trade_type=1)
        symbols.append(sym.strip())
        c += 1

    # Process short positions
    for sym in vshort.split(','):
        if sym.strip() == '':
            continue
        add_trade(symbol=sym.strip(), trade_date=vdate, trade_type=-1)
        symbols.append(sym.strip())
        c += 1
    print(f'{c} Trades added to DB')

    download_stock_data(symbols=symbols)

    for sym1 in symbols:
        atr, last_close = calculate_atr(sym1, vdate)
        update_atr(sym1, vdate, atr, last_close)
    return atr, c, last_close, sym, sym1, symbols, vdate, vlong, vshort


@app.cell
def _(mo):
    delete_trades_button = mo.ui.run_button(label='Delete all Trades')
    delete_trades_button
    return (delete_trades_button,)


@app.cell
def _(delete_all_trades, delete_trades_button, mo):
    mo.stop(not delete_trades_button.value)
    delete_all_trades()
    return


@app.cell
def _(pd):
    def trades_to_dataframe(trades):
        # Convert each trade to a dictionary and then build a DataFrame
            return pd.DataFrame([trade.model_dump() for trade in trades])
    return (trades_to_dataframe,)


@app.cell
def _(mo):
    update_prices_button = mo.ui.run_button(label='Update Prices')
    update_prices_button
    return (update_prices_button,)


@app.cell
def _(
    form1,
    get_all_trades,
    mo,
    symbols,
    trades_to_dataframe,
    update_prices_button,
    update_profit,
    vdate,
):
    import yfinance as yf

    mo.stop(not update_prices_button.value)
    mo.stop(form1.value == None)

    for sym3 in symbols:
    # Define the stock ticker symbol
       ticker_symbol = sym3  

       # Fetch the stock data
       stock = yf.Ticker(ticker_symbol)

       # Get today's historical data (1-day period)
       data = stock.history(period="1d")

       # Extract the open and current close prices
       open_price = data['Open'].iloc[0]
       current_close_price = data['Close'].iloc[0]

       update_profit(symbol=sym3, trade_date=vdate, open_price=open_price, close_price=current_close_price)

    trades = get_all_trades(vdate)  # or use any valid date
    dft = trades_to_dataframe(trades)
    dft.drop(columns=["trade_date", 'last_close', 'atr30', 'open', 'close', 'limit_touched', 'limit', 'notes' , 'id' ], inplace=True)
    dft
    return (
        current_close_price,
        data,
        dft,
        open_price,
        stock,
        sym3,
        ticker_symbol,
        trades,
        yf,
    )


@app.cell
def _(engine, mo, trade):
    _df = mo.sql(
        f"""
        SELECT symbol, profit, profit_original, gap_in_atr FROM trade
        """,
        engine=engine
    )
    return


@app.cell
def _(engine, mo, trade):
    _df = mo.sql(
        f"""
        SELECT sum(profit) FROM trade
        """,
        engine=engine
    )
    return


if __name__ == "__main__":
    app.run()
