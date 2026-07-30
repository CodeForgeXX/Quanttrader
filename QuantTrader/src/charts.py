import plotly.graph_objects as go

from src.indicators import ema, sma


def create_candlestick(
    df,
    symbol,
    entry=None,
    stop=None,
    tp1=None,
    tp2=None,
    tp3=None,
):

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name=symbol,
        )
    )

    df["EMA20"] = ema(df["Close"], 20)
    df["SMA20"] = sma(df["Close"], 20)

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["EMA20"],
            name="EMA20",
            line=dict(width=2, color="orange"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA20"],
            name="SMA20",
            line=dict(width=2, color="cyan"),
        )
    )

    if entry is not None:
        fig.add_hline(
            y=entry,
            line_color="blue",
            line_width=2,
            annotation_text="ENTRY",
        )

    if stop not in [None, "-"]:
        fig.add_hline(
            y=stop,
            line_color="red",
            line_width=2,
            annotation_text="STOP",
        )

    if tp1 not in [None, "-"]:
        fig.add_hline(
            y=tp1,
            line_color="green",
            annotation_text="TP1",
        )

    if tp2 not in [None, "-"]:
        fig.add_hline(
            y=tp2,
            line_color="green",
            line_dash="dot",
            annotation_text="TP2",
        )

    if tp3 not in [None, "-"]:
        fig.add_hline(
            y=tp3,
            line_color="green",
            line_dash="dash",
            annotation_text="TP3",
        )

    fig.update_layout(
        title=f"{symbol} Live Chart",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=700,
    )

    return fig