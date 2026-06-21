import re

with open("update_data.py", "r") as f:
    content = f.read()

# Replace hardcoded WATCHLIST with file read
old_watchlist = 'WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "MU"]'
new_watchlist = '''try:
    with open("watchlist.json", "r") as f:
        WATCHLIST = json.load(f)
except:
    WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "MU"]'''
content = content.replace(old_watchlist, new_watchlist)

# Replace prompt
old_prompt = '''    prompt = f"""You are a swing trading assistant. Analyze {ticker} currently at ${price:.2f}.
Recent price history (last 5 days): {history_summary}
The user does NOT do day trading and does NOT do options. 
Based on this simple data, provide a strict recommendation of BUY, SELL, or HOLD for a multi-week swing trade, and a 1-2 sentence justification.
Format your response exactly like this:
ACTION: [BUY/SELL/HOLD]
REASON: [Your 1-2 sentence reason]"""'''

new_prompt = '''    prompt = f"""You are a swing trading assistant. Analyze {ticker} currently at ${price:.2f}.
Recent price history (last 5 days): {history_summary}
The user does NOT do day trading and does NOT do options. 
Based on this simple data, provide a strict recommendation of BUY, SELL, or HOLD for a multi-week swing trade, a justification, and the sources/catalysts.
Format your response exactly like this:
ACTION: [BUY/SELL/HOLD]
REASON: [Your 1-2 sentence reason]
SOURCES: [List 1-2 key market drivers, news, catalysts, or technical levels backing this]"""'''
content = content.replace(old_prompt, new_prompt)

# Replace parsing logic
old_parse = '''        action = "HOLD"
        reason = "Analysis failed to parse."
        
        for line in content.split('\\n'):
            if line.startswith("ACTION:"):
                action = line.replace("ACTION:", "").strip()
            elif line.startswith("REASON:"):
                reason = line.replace("REASON:", "").strip()
                
        return action, reason'''

new_parse = '''        action = "HOLD"
        reason = "Analysis failed to parse."
        sources = "No specific sources provided."
        
        for line in content.split('\\n'):
            if line.startswith("ACTION:"):
                action = line.replace("ACTION:", "").strip()
            elif line.startswith("REASON:"):
                reason = line.replace("REASON:", "").strip()
            elif line.startswith("SOURCES:"):
                sources = line.replace("SOURCES:", "").strip()
                
        return action, reason, sources'''
content = content.replace(old_parse, new_parse)

# Replace return logic on error
content = content.replace('return "HOLD", f"Error during AI analysis: {e}"', 'return "HOLD", f"Error during AI analysis: {e}", "N/A"')
content = content.replace('return "HOLD", "API key missing. Defaulting to HOLD."', 'return "HOLD", "API key missing. Defaulting to HOLD.", "N/A"')

# Update usage of get_ai_analysis
content = content.replace('action, analysis = get_ai_analysis(ticker, current_price, history_summary)', 'action, analysis, sources = get_ai_analysis(ticker, current_price, history_summary)')

# Update dictionary appending
old_dict = '''        dashboard_data["watchlist"].append({
            "ticker": ticker,
            "price": f"{current_price:.2f}",
            "pct_change": f"{pct_change:+.2f}%",
            "action": action,
            "analysis": analysis
        })'''
new_dict = '''        dashboard_data["watchlist"].append({
            "ticker": ticker,
            "price": f"{current_price:.2f}",
            "pct_change": f"{pct_change:+.2f}%",
            "action": action,
            "analysis": analysis,
            "sources": sources
        })'''
content = content.replace(old_dict, new_dict)

old_dict2 = '''        dashboard_data["trending"].append({
            "ticker": ticker,
            "price": f"{item['price']:.2f}",
            "pct_change": f"{item['pct_change']:+.2f}%",
            "action": action,
            "analysis": analysis
        })'''
new_dict2 = '''        dashboard_data["trending"].append({
            "ticker": ticker,
            "price": f"{item['price']:.2f}",
            "pct_change": f"{item['pct_change']:+.2f}%",
            "action": action,
            "analysis": analysis,
            "sources": sources
        })'''
content = content.replace(old_dict2, new_dict2)

with open("update_data.py", "w") as f:
    f.write(content)
