import pandas as pd
import os
import sys

os.chdir('/Users/kunj/Documents/Python_Projects/IPL_Auction_Analysis')
os.getcwd()

df = pd.read_json('./Data/ball/335982.json')
