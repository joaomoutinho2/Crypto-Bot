def formatar_data(timestamp):
    from datetime import datetime
    return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')