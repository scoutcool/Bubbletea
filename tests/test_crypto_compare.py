import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import bubbletea

def test():
    result = bubbletea.load_historical_data('ETH', 'USD', 1619827200, 1619913600, '163b4f02ba446862200ecf7a64c3359b6d6bcf9d417aa27a0b5b29c9f9e619be', 1000)
    assert len(result) == 25
    result = bubbletea.load_historical_data('ETH', 'USD', 1619827200, 1619913600, '163b4f02ba446862200ecf7a64c3359b6d6bcf9d417aa27a0b5b29c9f9e619be', 6)
    assert len(result) == 25

if __name__ == "__main__":
    test()