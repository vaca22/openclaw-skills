#!/usr/bin/env python3
# stock.py - 股价查询脚本 (腾讯财经接口)
# 用法：python3 stock.py <股票代码或名称>

import sys
import re
import urllib.request

STOCK_MAP = {
    '顺丰控股': 'sz002352', '顺丰': 'sz002352',
    '腾讯控股': 'hk00700', '腾讯': 'hk00700',
    '阿里巴巴': 'hk09988', '阿里': 'hk09988',
    '苹果': 'usAAPL', 'AAPL': 'usAAPL',
    '特斯拉': 'usTSLA', 'TSLA': 'usTSLA',
    '茅台': 'sh600519', '贵州茅台': 'sh600519',
}

def get_stock_code(query):
    query = query.strip().upper()
    if query in STOCK_MAP or query.lower() in {k.lower() for k in STOCK_MAP}:
        for k, v in STOCK_MAP.items():
            if k.lower() == query.lower(): return v
    if re.match(r'^(sz|sh|hk|us)[0-9A-Za-z]+$', query, re.IGNORECASE): return query.lower()
    if re.match(r'^[0-9]{6}$', query): return f'sz{query}'
    return None

def fetch_stock_data(code):
    url = f"https://qt.gtimg.cn/q={code}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gbk', errors='ignore')
        return parse_tx_data(data, code)
    except Exception as e:
        print(f"❌ 请求失败：{e}")
        return None

def parse_tx_data(raw_data, code):
    match = re.search(r'="([^"]+)"', raw_data)
    if not match: return None
    fields = match.group(1).split('~')
    if len(fields) < 30: return None
    
    data = {
        'name': fields[1] if len(fields) > 1 else code,
        'code': fields[2] if len(fields) > 2 else code,
        'price': fields[3] if len(fields) > 3 else '',
        'pre_close': fields[4] if len(fields) > 4 else '',
        'open': fields[5] if len(fields) > 5 else '',
        'volume': fields[6] if len(fields) > 6 else '',
        'amount': fields[7] if len(fields) > 7 else '',
        'high': fields[33] if len(fields) > 33 else '',
        'low': fields[34] if len(fields) > 34 else '',
        'timestamp': fields[30] if len(fields) > 30 else '',
        'total_market_cap': fields[44] if len(fields) > 44 else '',
        'float_market_cap': fields[45] if len(fields) > 45 else '',
        'pe_ratio': fields[48] if len(fields) > 48 else '',
        'turnover_rate': fields[56] if len(fields) > 56 else '',
    }
    
    if data['price'] and data['pre_close']:
        try:
            price = float(data['price'])
            pre_close = float(data['pre_close'])
            change = price - pre_close
            change_pct = (change / pre_close) * 100
            data['change'] = f"{change:+.2f}"
            data['change_pct'] = f"{change_pct:+.2f}"
        except: pass
    return data

def format_output(data):
    if not data:
        print("❌ 未获取到数据")
        return
    print(f"\n## 📊 {data['name']} ({data['code']})\n")
    print("| 项目 | 数值 |")
    print("|------|------|")
    if data['price']: print(f"| **当前价** | **{data['price']} 元** |")
    if data.get('change') and data.get('change_pct'): print(f"| 涨跌 | {data['change']} ({data['change_pct']}%) |")
    if data['open']: print(f"| 今开 | {data['open']} 元 |")
    if data['high']: print(f"| 最高 | {data['high']} 元 |")
    if data['low']: print(f"| 最低 | {data['low']} 元 |")
    if data['pre_close']: print(f"| 昨收 | {data['pre_close']} 元 |")
    if data['volume']:
        try: print(f"| 成交量 | {float(data['volume'])/10000:.2f} 万手 |")
        except: print(f"| 成交量 | {data['volume']} |")
    if data['amount']:
        try: print(f"| 成交额 | {float(data['amount'])/10000:.2f} 亿元 |")
        except: print(f"| 成交额 | {data['amount']} |")
    if data['total_market_cap']:
        try: print(f"| 总市值 | {float(data['total_market_cap']):.2f} 亿 |")
        except: print(f"| 总市值 | {data['total_market_cap']} |")
    if data['float_market_cap']:
        try: print(f"| 流通市值 | {float(data['float_market_cap']):.2f} 亿 |")
        except: print(f"| 流通市值 | {data['float_market_cap']} |")
    if data['pe_ratio']: print(f"| 市盈率 (TTM) | {data['pe_ratio']} |")
    if data['turnover_rate']:
        try: print(f"| 换手率 | {float(data['turnover_rate']):.2f}% |")
        except: print(f"| 换手率 | {data['turnover_rate']} |")
    if data['timestamp']:
        ts = data['timestamp']
        if len(ts) >= 14 and ts[:4].isdigit(): print(f"| 数据时间 | {ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}:{ts[12:14]} |")
        else: print(f"| 数据时间 | {ts} |")
    print("\n---")
    print("💡 **数据来源**: 腾讯财经实时接口 (免费，无需 API Key)")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python3 stock.py <股票代码或名称>")
        print("示例：python3 stock.py 顺丰控股")
        sys.exit(1)
    code = get_stock_code(sys.argv[1])
    if not code:
        print(f"❌ 无法识别股票：{sys.argv[1]}")
        sys.exit(1)
    data = fetch_stock_data(code)
    format_output(data)
