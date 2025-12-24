"""
Helper utility functions
"""
from datetime import datetime
from typing import Union


def format_currency(value: Union[int, float], currency: str = "$") -> str:
    """
    Format number as currency
    
    Args:
        value: Numeric value
        currency: Currency symbol
    
    Returns:
        Formatted string
    """
    try:
        if value >= 1_000_000:
            return f"{currency}{value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{currency}{value/1_000:.2f}K"
        else:
            return f"{currency}{value:,.2f}"
    except:
        return f"{currency}0.00"


def format_percentage(value: Union[int, float], decimals: int = 1) -> str:
    """
    Format number as percentage
    
    Args:
        value: Numeric value (0-100 or 0-1)
        decimals: Number of decimal places
    
    Returns:
        Formatted string
    """
    try:
        # If value is between 0 and 1, assume it's a decimal
        if 0 <= value <= 1:
            value = value * 100
        return f"{value:.{decimals}f}%"
    except:
        return "0.0%"


def format_number(value: Union[int, float], decimals: int = 0) -> str:
    """
    Format number with thousands separator
    
    Args:
        value: Numeric value
        decimals: Number of decimal places
    
    Returns:
        Formatted string
    """
    try:
        if decimals == 0:
            return f"{int(value):,}"
        else:
            return f"{value:,.{decimals}f}"
    except:
        return "0"


def format_date(date_str: str, output_format: str = "%Y-%m-%d") -> str:
    """
    Format date string
    
    Args:
        date_str: Date string
        output_format: Desired output format
    
    Returns:
        Formatted date string
    """
    try:
        # Try common date formats
        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime(output_format)
            except:
                continue
        return date_str
    except:
        return date_str


def get_risk_emoji(risk_level: str) -> str:
    """
    Get emoji for risk level
    
    Args:
        risk_level: Risk level (low, medium, high)
    
    Returns:
        Emoji string
    """
    risk_emojis = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🔴'
    }
    return risk_emojis.get(risk_level.lower(), '⚪')


def get_priority_emoji(priority: str) -> str:
    """
    Get emoji for priority level
    
    Args:
        priority: Priority level (low, medium, high)
    
    Returns:
        Emoji string
    """
    priority_emojis = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🔴'
    }
    return priority_emojis.get(priority.lower(), '⚪')


def get_success_emoji(probability: float) -> str:
    """
    Get emoji for success probability
    
    Args:
        probability: Success probability (0-100)
    
    Returns:
        Emoji string
    """
    if probability >= 70:
        return '🟢'
    elif probability >= 50:
        return '🟡'
    else:
        return '🔴'


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to max length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change
    
    Args:
        old_value: Old value
        new_value: New value
    
    Returns:
        Percentage change
    """
    try:
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100
    except:
        return 0


def get_metric_color(value: float, threshold_good: float, threshold_bad: float, higher_is_better: bool = True) -> str:
    """
    Get color based on metric value and thresholds
    
    Args:
        value: Metric value
        threshold_good: Good threshold
        threshold_bad: Bad threshold
        higher_is_better: If True, higher values are better
    
    Returns:
        Color name
    """
    if higher_is_better:
        if value >= threshold_good:
            return 'success'
        elif value >= threshold_bad:
            return 'warning'
        else:
            return 'danger'
    else:
        if value <= threshold_good:
            return 'success'
        elif value <= threshold_bad:
            return 'warning'
        else:
            return 'danger'


def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """
    Safely divide two numbers
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division fails
    
    Returns:
        Result of division or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default
