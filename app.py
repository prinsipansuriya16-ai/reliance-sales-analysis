import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="stock market Trading Dashboard", layout="wide")

st.title("📊 Reliance Live Technical Analytics Dashboard")
st.write("this dashboard shows close price , close vs mean_20 vs mean_50 price ,year wise monthly average price , RSI and MACD signals.")
 
try:
    df = pd.read_csv("Reliance.csv")
    df['Date'] = pd.to_datetime(df['Date'])

    df['mean_20'] = df['Close'].rolling(window=20).mean()
    df['mean_50'] = df['Close'].rolling(window=50).mean()

    diffrance = df['Close'].diff()

    gain = diffrance.where(diffrance>0 , 0)
    loss = - diffrance.where(diffrance<0 , 0)

    avg_gain = gain.rolling(window=14).mean() 
    avg_loss = loss.rolling(window=14).mean() 
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1+rs))
    df['RSI'] = rsi

    #  MACD CALCULATION

    # .ewm() (Exponential Weighted Moving)

    # EMA (Exponential Moving Average)

    df['EMA_12'] = df['Close'].ewm(span=12 , adjust=False).mean()
    df['EMA_28'] = df['Close'].ewm(span=28 , adjust=False).mean()

    df['MACD_line'] = df['EMA_12'] - df['EMA_28']

    df['signal_line'] = df['MACD_line'].ewm(span=9 , adjust=False).mean()

    df['MACD_histogram'] = df['MACD_line'] - df['signal_line']  

    df[['EMA_12', 'EMA_28' , 'MACD_line' , 'signal_line' , 'MACD_histogram']] 

    #   yearly calculation
    df['year'] = df['Date'].dt.year
    df['Month_Num'] = df['Date'].dt.month

    year_avg = df.groupby(by=['year', 'Month_Num'])['Close'].mean().reset_index()
    

    def month(x):
        m = { 1:'january' , 2:'february' , 3:'march' , 4:'april' , 5:'may' , 6: 'june' , 7:'july' , 8:'august',
                    9:'september' , 10:'october' , 11:'november' , 12:'december' }
    
        return m.get(x , "invalid number")

    year_avg['month name'] = pd.DataFrame(year_avg['Month_Num'].apply(month))
    year_avg['month-year'] = year_avg['month name'] + '-' + year_avg['year'].astype(str)
    year_avg = year_avg.sort_values(by=['year', 'Month_Num'])
    # close_2020 = year_avg[year_avg['year'] == 2020].sort_values(by='Month_Num')


except FileNotFoundError:
    st.error("❌ file not found.")
    st.stop()

# ==========================================
# 2. SIDEBAR WIDGET
# ==========================================
st.sidebar.header("🛠️ Dashboard Settings")
indicator_choice = st.sidebar.selectbox(
    "what graph you want to show?",
    ["closing price" , "close VS mean_20 VS mean_50" , "year wise monthly average","RSI graph" , "MACD graph" ,"RSI and MACD"]
)

# ==========================================
# 3. PLOTLY GRAPHS GENERATION (Naam updated)
# ==========================================

# --- close---
fig_close = go.Figure()
fig_close.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Closing price', line=dict(color='red')))
fig_close.update_layout(title='closing information' , xaxis_title="date/year" , yaxis_title="price($)" , template='plotly_dark',hovermode='x unified')

# ----close price per year----
fig_year = go.Figure()
fig_year.add_trace(go.Scatter(x=year_avg['month-year'], y=year_avg['Close'], mode='lines', name='Closing price', line=dict(color='red')))
fig_year.update_layout(title='closing information' , xaxis_title="date/year" , yaxis_title="price($)" , template='plotly_dark',hovermode='x unified')

# ------close,mean-20,mean-50
fig_mean = go.Figure()
fig_mean.add_trace(go.Scatter(x=df['Date'],y=df['Close'],mode='lines',name='closing price',line=dict(color='red')))
fig_mean.add_trace(go.Scatter(x=df['Date'],y=df['mean_20'],mode='lines',name='mean of 20 days',line=dict(color='green',width=2, dash='dot')))
fig_mean.add_trace(go.Scatter(x=df['Date'],y=df['mean_50'],mode='lines',name='mean of 50 days',line=dict(color='orange',width=2, dash='dot')))
fig_mean.update_layout(title='close VS mean_20 VS mean_20' , xaxis_title="date/year" , yaxis_title="price($)" , template='plotly_dark',hovermode='x unified')


# --- RSI ---
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], mode='lines', name='RSI', line=dict(color='purple')))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red") #overbought
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green") #oversell
fig_rsi.update_layout(title="RSI (Overbought/Oversold Index)", template='plotly_dark', hovermode='x unified', yaxis_title='RSI' , xaxis_title="date/year")


# -----MACD-----
colors = ['green' if val >= 0 else 'red' for val in df['MACD_histogram']]
fig_MACD = go.Figure()
fig_MACD.add_trace(go.Scatter(x=df['Date'] ,y=df['MACD_line'],mode='lines',name='MACD_line',line=dict(color="red")))
fig_MACD.add_trace(go.Scatter(x=df['Date'] ,y=df['signal_line'],mode='lines',name='SIGNAL_line',line=dict(color="blue",width=2, dash='dot')))
fig_MACD.add_trace(go.Bar(x=df['Date'] ,y=df['MACD_histogram'],name='Histogram',marker=dict(color=colors, opacity=1.0) ))
fig_MACD.update_layout(title="MACD information", template='plotly_dark', hovermode='x unified', yaxis_title='price($)' , xaxis_title="date/year")

# ==========================================
# 4. DISPLAY LOGIC
# ==========================================
if indicator_choice == "closing price":
    st.subheader("📈 closing price Analysis")
    st.plotly_chart(fig_close,  use_container_width=True)

elif indicator_choice == "close VS mean_20 VS mean_50":
    st.subheader("📉 close VS mean_20 VS mean_50 Analysis")
    st.plotly_chart(fig_mean, use_container_width=True)

elif indicator_choice == "RSI and MACD":
    st.subheader("📈 RSI and MACD Analysis")
    st.plotly_chart(fig_rsi, use_container_width=True)
    st.subheader("📉 RSI Analysis")
    st.plotly_chart(fig_MACD, use_container_width=True)

elif indicator_choice == "RSI graph":
    st.subheader("📉 RSI graph Analysis")
    st.plotly_chart(fig_rsi, use_container_width=True)

elif indicator_choice == "MACD graph":
    st.subheader("📉 MACD graph Analysis")
    st.plotly_chart(fig_MACD, use_container_width=True)

elif indicator_choice == "year wise monthly average":
    st.subheader("📉 year wise monthly average Analysis")
    st.plotly_chart(fig_year, use_container_width=True)
