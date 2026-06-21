import os
import json
import datetime
import yfinance as yf
import requests


# Configuration
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"] # Add your preferred tickers here
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
        return "HOLD", "API key missing. Defaulting to HOLD."
    
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""You are a swing trading assistant. Analyze {ticker} currently at ${price:.2f}.
Recent price history (last 5 days): {history_summary}
The user does NOT do day trading and does NOT do options. 
Based on this simple data, provide a strict recommendation of BUY, SELL, or HOLD for a multi-week swing trade, and a 1-2 sentence justification.
Format your response exactly like this:
ACTION: [BUY/SELL/HOLD]
REASON: [Your 1-2 sentence reason]"""

    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        content = response.text
        action = "HOLD"
        reason = "Analysis failed to parse."
        
        for line in content.split('\n'):
            if line.startswith("ACTION:"):
                action = line.replace("ACTION:", "").strip()
            elif line.startswith("REASON:"):
                reason = line.replace("REASON:", "").strip()
                
        return action, reason
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return "HOLD", "Error during AI analysis."

def main():
    dashboard_data = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "stocks": []
    }
    
    telegram_summary = "📈 <b>Daily Swing Trading Update</b>\n\n"
    
    for ticker in TICKERS:
        print(f"Processing {ticker}...")
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        
        if hist.empty:
            continue
            
        current_price = hist['Close'].iloc[-1]
        history_summary = ", ".join([f"{date.strftime('%m-%d')}: ${price:.2f}" for date, price in zip(hist.index, hist['Close'])])
        
        action, analysis = get_ai_analysis(ticker, current_price, history_summary)
        
        dashboard_data["stocks"].append({
            "ticker": ticker,
            "price": f"{current_price:.2f}",
            "action": action,
            "analysis": analysis
        })
        
        # Add to telegram summary if actionable (minimize spam)
        if action in ["BUY", "SELL"]:
            telegram_summary += f"<b>{ticker}</b>: {action} at ${current_price:.2f}\n{analysis}\n\n"
            
    # Save dashboard data
    with open("data.json", "w") as f:
        json.dump(dashboard_data, f, indent=2)
        
    # Send notification if there's anything to do
    if "BUY" in telegram_summary or "SELL" in telegram_summary:
        telegram_summary += f"\n<a href='https://{os.environ.get('GITHUB_REPOSITORY_OWNER')}.github.io/stock-swing-dashboard/'>View Full Dashboard</a>"
        send_telegram_message(telegram_summary)
    else:
        # Just to confirm it ran if everything is hold
        send_telegram_message("📈 Daily Update: All tracked stocks are currently a HOLD. No action needed.")

if __name__ == "__main__":
    main()