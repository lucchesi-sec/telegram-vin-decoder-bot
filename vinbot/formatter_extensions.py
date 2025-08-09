"""Extended formatters for market value and history data"""

from typing import Any, Dict
from datetime import datetime


def format_market_value(data: Dict[str, Any]) -> str:
    """Format market value information"""
    marketvalue = data.get("marketvalue", {})
    
    if not marketvalue:
        return "💰 **MARKET VALUE**\n\nNo market value data available for this vehicle."
    
    lines = ["💰 **MARKET VALUE**", "=" * 30, ""]
    
    # MSRP and Retail
    msrp = marketvalue.get("msrp")
    retail = marketvalue.get("retail")
    
    if msrp:
        lines.append(f"**Original MSRP:** ${msrp:,}")
    if retail:
        lines.append(f"**Current Retail Value:** ${retail:,}")
    
    if msrp and retail:
        depreciation = msrp - retail
        depreciation_pct = (depreciation / msrp) * 100
        lines.append(f"**Depreciation:** ${depreciation:,} ({depreciation_pct:.1f}%)")
    
    lines.append("")
    
    # Trade-in Values
    lines.append("📊 **TRADE-IN VALUES**")
    lines.append("-" * 20)
    
    trade_in = marketvalue.get("tradeIn")
    avg_trade = marketvalue.get("averageTradeIn")
    rough_trade = marketvalue.get("roughTradeIn")
    
    if trade_in:
        lines.append(f"**Clean Trade-In:** ${trade_in:,}")
    if avg_trade:
        lines.append(f"**Average Trade-In:** ${avg_trade:,}")
    if rough_trade:
        lines.append(f"**Rough Trade-In:** ${rough_trade:,}")
    
    # Loan Value
    loan_value = marketvalue.get("loanValue")
    if loan_value:
        lines.append(f"**Loan Value:** ${loan_value:,}")
    
    # Auction Values
    auction = marketvalue.get("auctionValues", {})
    if auction:
        lines.append("\n🔨 **AUCTION VALUES**")
        lines.append("-" * 20)
        
        low_auction = auction.get("lowAuctionValue")
        avg_auction = auction.get("averageAuctionValue")
        high_auction = auction.get("highAuctionValue")
        date_range = auction.get("dateRange")
        
        if low_auction:
            lines.append(f"**Low:** ${low_auction:,}")
        if avg_auction:
            lines.append(f"**Average:** ${avg_auction:,}")
        if high_auction:
            lines.append(f"**High:** ${high_auction:,}")
        if date_range:
            lines.append(f"**As of:** {date_range}")
    
    # Get VIN from main data
    vin = data.get("attributes", {}).get("vin") or data.get("vin")
    if vin:
        lines.append(f"\n`{vin}`")
    
    return "\n".join(lines)


def format_history(data: Dict[str, Any]) -> str:
    """Format vehicle history information"""
    history = data.get("history", {})
    
    if not history:
        return "📜 **VEHICLE HISTORY**\n\nNo history data available for this vehicle."
    
    lines = ["📜 **VEHICLE HISTORY**", "=" * 30, ""]
    
    # Current Title Information
    current_title = history.get("currentTitleInformation", [])
    if current_title and len(current_title) > 0:
        current = current_title[0]
        lines.append("📋 **CURRENT TITLE**")
        lines.append("-" * 20)
        
        state = current.get("TitleIssuingAuthorityName", "Unknown")
        lines.append(f"**State:** {state}")
        
        issue_date = current.get("TitleIssueDate", {}).get("Date")
        if issue_date:
            try:
                date_obj = datetime.fromisoformat(issue_date.replace("Z", "+00:00"))
                lines.append(f"**Issue Date:** {date_obj.strftime('%B %d, %Y')}")
            except:
                lines.append(f"**Issue Date:** {issue_date}")
        
        odometer = current.get("VehicleOdometerReadingMeasure")
        if odometer:
            try:
                miles = int(odometer)
                lines.append(f"**Odometer:** {miles:,} miles")
            except:
                lines.append(f"**Odometer:** {odometer} miles")
    
    # Title History
    history_info = history.get("historyInformation", [])
    if history_info:
        lines.append("\n📚 **TITLE HISTORY**")
        lines.append("-" * 20)
        
        for i, record in enumerate(history_info, 1):
            state = record.get("TitleIssuingAuthorityName", "Unknown")
            issue_date = record.get("TitleIssueDate", {}).get("Date")
            odometer = record.get("VehicleOdometerReadingMeasure")
            
            date_str = ""
            if issue_date:
                try:
                    date_obj = datetime.fromisoformat(issue_date.replace("Z", "+00:00"))
                    date_str = date_obj.strftime("%m/%d/%Y")
                except:
                    date_str = issue_date
            
            miles_str = ""
            if odometer:
                try:
                    miles = int(odometer)
                    miles_str = f" - {miles:,} miles"
                except:
                    miles_str = f" - {odometer} miles"
            
            lines.append(f"**{i}.** {state} ({date_str}){miles_str}")
    
    # Brands Information (Clear, Salvage, etc.)
    brands_count = history.get("brandsRecordCount", 0)
    if brands_count == 0:
        lines.append("\n✅ **TITLE STATUS:** Clear (No brands)")
    else:
        lines.append(f"\n⚠️ **TITLE BRANDS:** {brands_count} record(s)")
    
    # Junk/Salvage Information
    junk_salvage = history.get("junkAndSalvageInformation", [])
    if junk_salvage:
        lines.append("\n⚠️ **SALVAGE/JUNK RECORDS**")
        lines.append("-" * 20)
        for record in junk_salvage[:3]:  # Limit to first 3
            lines.append(f"• {record}")
    
    # Insurance Information
    insurance = history.get("insuranceInformation", [])
    if insurance:
        lines.append("\n🛡️ **INSURANCE RECORDS**")
        lines.append("-" * 20)
        for record in insurance[:3]:  # Limit to first 3
            lines.append(f"• {record}")
    
    # Get VIN from main data
    vin = data.get("attributes", {}).get("vin") or history.get("vin")
    if vin:
        lines.append(f"\n`{vin}`")
    
    return "\n".join(lines)