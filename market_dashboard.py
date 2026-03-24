import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global Asset Tracker", layout="wide")
st.title("💎 Global Asset Pulse: 1-Year Performance")

# 🗄️ Asset groups
ASSETS = {
    "Commodities": {"Gold": "GC=F", "Silver": "SI=F", "Crude Oil": "CL=F"},
    "Crypto": {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD", "XRP": "XRP-USD"},
    "Market Indices": {"S&P 500": "^GSPC", "Nasdaq": "^IXIC"},
    "Forex": {"NZD/USD": "NZDUSD=X", "USD/CNY": "USDCNY=X", "AUD/NZD": "AUDNZD=X"},
    "Tech & AI": {
        "Nvidia": "NVDA", 
        "Micron": "MU", 
        "Sandisk (WDC)": "WDC", 
        "Rocket Lab": "RKLB"
    },
    "Semiconductors (Korea)": {
        "Samsung": "005930.KS", 
        "SK Hynix": "000660.KS"
    }
}

@st.cache_data(ttl=3600)
def get_market_data():
    all_tickers = []
    for cat in ASSETS.values():
        all_tickers.extend(cat.values())
    
    # Fetch 1 year of DAILY data
    data = yf.download(all_tickers, period="1y", interval="1d")
    
    if 'Close' in data.columns:
        return data['Close']
    return data

data = get_market_data()

# --- UI LAYOUT ---
for category, items in ASSETS.items():
    st.subheader(f"📂 {category}")
    
    num_items = len(items)
    cols = st.columns(num_items)
    
    # 📏 DYNAMIC HEIGHT LOGIC
    # More items in a row = shorter graphs to prevent vertical scrolling fatigue
    if num_items == 2:
        chart_height = 350
    elif num_items == 3:
        chart_height = 250
    else:
        chart_height = 180
    
    for i, (name, ticker) in enumerate(items.items()):
        if ticker in data.columns:
            series = data[ticker].dropna()
            
            if not series.empty:
                current_price = series.iloc[-1]
                prev_day_price = series.iloc[-2]
                day_delta = ((current_price - prev_day_price) / prev_day_price) * 100
                
                year_start_price = series.iloc[0]
                year_delta = ((current_price - year_start_price) / year_start_price) * 100
                
                with cols[i]:
                    with st.container(border=True):
                        st.metric(
                            label=name,
                            value=f"${current_price:,.2f}" if category != "Forex" else f"{current_price:.4f}",
                            delta=f"{day_delta:+.2f}% (Day)"
                        )
                        
                        # Apply the dynamic height here
                        fig = px.line(
                            series, 
                            template="plotly_white", 
                            height=chart_height 
                        )
                        
                        fig.update_xaxes(visible=False)
                        fig.update_yaxes(title_text=None, tickprefix="$" if category != "Forex" else "")
                        fig.update_layout(
                            margin=dict(l=5, r=5, t=5, b=5),
                            hovermode="x unified",
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        st.caption(f"**1Y Return: {year_delta:+.1f}%**")

st.info("💡 Tip: Hover over any chart to see the specific price on that date.")