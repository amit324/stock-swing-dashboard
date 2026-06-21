import os
import json
import datetime
import yfinance as yf
import requests

# Configuration
# 1. Watchlist: You will get Telegram notifications for these if there's a BUY/SELL signal.
try:
    with open("watchlist.json", "r") as f:
        WATCHLIST = json.load(f)
except:
    WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "MU"] 

# 2. Discovery Candidates: The script will check these to find top "Trending" (biggest % gainers over 5 days) to show on the dashboard.
TRENDING_CANDIDATES = [
    "NVDA", "AMD", "TSLA", "NFLX", "SMCI", "AVGO", "CRWD", 
    "PLTR", "ARM", "INTC", "QCOM", "SNOW", "UBER", "COIN", "HOOD", "SQ"
]

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing, skipping notification.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def get_ai_analysis(ticker, price, history_summary):
    if not GEMINI_API_KEY:
        return "HOLD", "API key missing. Defaulting to HOLD.", "N/A"
    
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""You are a swing trading assistant. Analyze {ticker} currently at ${price:.2f}.
Recent price history (last 5 days): {history_summary}
The user does NOT do day trading and does NOT do options. 
Based on this simple data, provide a strict recommendation of BUY, SELL, or HOLD for a multi-week swing trade, a justification, and the sources/catalysts.
Format your response exactly like this:
ACTION: [BUY/SELL/HOLD]
REASON: [Your 1-2 sentence reason]
SOURCES: [List 1-2 key market drivers, news, catalysts, or technical levels backing this]"""

    try:
        models_to_try = ['gemini-3.1-flash', 'gemini-3.0-flash', 'gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
        response = None
        for m in models_to_try:
            try:
                response = client.models.generate_content(model=m, contents=prompt)
                break
            except Exception as e:
                print(f"Model {m} failed: {e}")
                
        if not response:
            raise Exception("All Gemini models failed")
            
        content = response.text
        action = "HOLD"
        reason = "Analysis failed to parse."
        sources = "No specific sources provided by the model."
        
        import re
        action_match = re.search(r'ACTION:\s*([^\n]+)', content, re.IGNORECASE)
        reason_match = re.search(r'REASON:\s*(.*?)(?=\nSOURCES:|$)', content, re.IGNORECASE | re.DOTALL)
        sources_match = re.search(r'SOURCES:\s*(.*)', content, re.IGNORECASE | re.DOTALL)
        
        if action_match:
            action = action_match.group(1).strip().replace("**", "").replace("*", "")
        if reason_match:
            reason = reason_match.group(1).strip().replace("**", "")
        if sources_match:
            sources = sources_match.group(1).strip().replace("**", "")
            
        return action, reason, sources
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return "HOLD", f"Error during AI analysis: {e}", "N/A"

def main():
    dashboard_data = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "watchlist": [],
        "trending": []
    }
    
    telegram_summary = "📈 <b>Watchlist Swing Update</b>\n\n"
    notify = False
    
    # 1. Process Watchlist
    print("Processing Watchlist...")
    for ticker in WATCHLIST:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if hist.empty or len(hist) < 2:
            continue
            
        current_price = hist['Close'].iloc[-1]
        start_price = hist['Close'].iloc[0]
        pct_change = ((current_price - start_price) / start_price) * 100
        history_summary = ", ".join([f"{date.strftime('%m-%d')}: ${price:.2f}" for date, price in zip(hist.index, hist['Close'])])
        
        action, analysis, sources = get_ai_analysis(ticker, current_price, history_summary)
        
        dashboard_data["watchlist"].append({
            "ticker": ticker,
            "price": f"{current_price:.2f}",
            "pct_change": f"{pct_change:+.2f}%",
            "action": action,
            "analysis": analysis,
            "sources": sources
        })
        
        if action in ["BUY", "SELL"]:
            telegram_summary += f"<b>{ticker}</b>: {action} at ${current_price:.2f} ({pct_change:+.2f}%)\n{analysis}\n\n"
            notify = True

    # 2. Process Trending Candidates
    print("Finding Trending Stocks...")
    candidate_data = []
    for ticker in TRENDING_CANDIDATES:
        if ticker in WATCHLIST:
            continue
            
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if hist.empty or len(hist) < 2:
            continue
            
        current_price = hist['Close'].iloc[-1]
        start_price = hist['Close'].iloc[0]
        pct_change = ((current_price - start_price) / start_price) * 100
        history_summary = ", ".join([f"{date.strftime('%m-%d')}: ${price:.2f}" for date, price in zip(hist.index, hist['Close'])])
        
        candidate_data.append({
            "ticker": ticker,
            "price": current_price,
            "pct_change": pct_change,
            "history_summary": history_summary
        })
        
    # Sort candidates by highest 5-day percentage gain
    candidate_data.sort(key=lambda x: x["pct_change"], reverse=True)
    top_trending = candidate_data[:5] # Take top 5
    
    for item in top_trending:
        ticker = item["ticker"]
        action, analysis = get_ai_analysis(ticker, item["price"], item["history_summary"])
        dashboard_data["trending"].append({
            "ticker": ticker,
            "price": f"{item['price']:.2f}",
            "pct_change": f"{item['pct_change']:+.2f}%",
            "action": action,
            "analysis": analysis,
            "sources": sources
        })
            
    # Save dashboard data
    with open("data.json", "w") as f:
        json.dump(dashboard_data, f, indent=2)
        
    # Send notification if watchlist has actionable items
    if notify:
        telegram_summary += f"<a href='https://{os.environ.get('GITHUB_REPOSITORY_OWNER')}.github.io/stock-swing-dashboard/'>View Full Dashboard</a>"
        send_telegram_message(telegram_summary)
    else:
        send_telegram_message("📈 Daily Update: Watchlist stocks are all HOLD. Check the dashboard to see trending stocks!")

if __name__ == "__main__":
    main()
