
"""
  script to download klines.
  set the absoluate path destination folder for STORE_DIRECTORY, and run

  e.g. STORE_DIRECTORY=/ ./download-kline.py

"""
#import sys
import os
from os.path import exists
import requests #for checking if it is downloadable see https://stackoverflow.com/questions/61629856/how-to-check-whether-a-url-is-downloadable-or-not
from datetime import *
import pandas as pd
from enums import *
from utility import download_file, get_all_symbols, get_parser, get_start_end_date_objects, convert_to_date_object, \
  get_path
import zipfile

START_DATE="2017-01"
END_DATE = str(datetime.now().year)+"-"+str(datetime.now().month-1)
if datetime.now().month == 1: #if we are in January then we go to December lat year
  END_DATE = str(datetime.now().year-1)+"-"+str(12)

def download_monthly_klines(trading_type, symbols, num_symbols, intervals, years, months, start_date, end_date, folder, checksum):
  current = 0
  date_range = None

  if start_date and end_date:
    date_range = start_date + " " + end_date

#
  if float(end_date.split('-')[0]) >= float(END_DATE.split('-')[0]):
    if float(end_date.split('-')[1]) >= float(END_DATE.split('-')[1]):
      end_date = END_DATE

  start_date = start_date + '-01'#for strptime
  if not start_date:
    start_date = START_DATE
  else:
    start_date = datetime.strptime(start_date,'%Y-%m-%d').date()

  end_date = end_date + '-01'#for 
  if not end_date:
    end_date = END_DATE
  else:
    end_date = datetime.strptime(end_date,'%Y-%m-%d').date()

  print("Found {} symbols".format(num_symbols))

  for symbol in symbols:
    print("[{}/{}] - start download monthly {} klines ".format(current+1, num_symbols, symbol))
    for interval in intervals:
      for year in reversed(years):
        for month in reversed(months):
          current_date = convert_to_date_object('{}-{}-01'.format(year, month))
          if current_date >= start_date and current_date <= end_date:
            path = get_path(trading_type, "klines", "monthly", symbol, interval)
            file_name = "{}-{}-{}-{}".format(symbol.upper(), interval, year, '{:02d}'.format(month))
            path_to_file = folder+path+file_name
            if exists(path_to_file+'.csv'):
              print(path_to_file,".csv already exists")
              continue
            #We rewrite the path with \\ only
            path_to_zip_file = path_to_file.replace('/','\\')+".zip"
            if os.path.isfile(path_to_zip_file):
              print(path_to_zip_file," already exists so we remove it, redownload a cleaner version")
              os.remove(path_to_zip_file)
            #we start the download and if the download does not occur
            if not download_file(path, file_name+'.zip', '', folder):
              break
            #We rewrite the path with \\ only
            # if not exists(path_to_zip_file):
            #   print("no zip exists on database")#other method https://stackoverflow.com/questions/16778435/python-check-if-website-exists
            #   break
            with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
                zip_ref.extractall(folder+path)
                zip_ref.close()#need to close before removing
                os.remove(path_to_zip_file)

            if checksum == 1:
              checksum_path = get_path(trading_type, "klines", "monthly", symbol, interval)
              checksum_file_name = "{}-{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, year, '{:02d}'.format(month))
              download_file(checksum_path, checksum_file_name, '', folder)
    
    current += 1

def download_daily_klines(trading_type, symbols, num_symbols, intervals, dates, start_date, end_date, folder, checksum):
  current = 0
  date_range = None

  if start_date and end_date:
    date_range = start_date + " " + end_date

  start_date = start_date + '-01'#for strptime
  if not start_date:
    start_date = START_DATE
  else:
    start_date = datetime.strptime(start_date,'%Y-%m-%d').date()

  end_date = end_date + '-01'#for 
  if not end_date:
    end_date = END_DATE
  else:
    end_date = datetime.strptime(end_date,'%Y-%m-%d').date()

  #Get valid intervals for daily
  intervals = list(set(intervals) & set(DAILY_INTERVALS))#A \cap B
  print("Found {} symbols".format(num_symbols))

  for symbol in symbols:
    print("[{}/{}] - start download daily {} klines ".format(current+1, num_symbols, symbol))
    for interval in intervals:
      for date in dates:
        current_date = convert_to_date_object(date)
        if current_date >= start_date and current_date <= end_date:
          path = get_path(trading_type, "klines", "daily", symbol, interval)
          file_name = "{}-{}-{}.zip".format(symbol.upper(), interval, date)
          download_file(path, file_name, date_range, folder)
          path_to_zip = folder+path+file_name
          with zipfile.ZipFile(path_to_zip, 'r') as zip_ref:
              zip_ref.extractall(folder+path)
              zip_ref.close()#need to close before removing
              os.remove(path_to_zip)

          if checksum == 1:
            checksum_path = get_path(trading_type, "klines", "daily", symbol, interval)
            checksum_file_name = "{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, date)
            download_file(checksum_path, checksum_file_name, date_range, folder)

    current += 1


#TEST
if __name__ == "__main__":
    #Exemple
    folder = "C:/Users/benig/Documents/Projects/TradingBot/"
    year = [2020]
    month = [5]
    symbols = ["BTCUSDT"]
    num_symbols = len(symbols)
    trading_type = 'spot'
    intervals = ['1d']
    startDate = "2018-05"
    endDate = "2021-08"
    checksum = True

    download_monthly_klines(trading_type, symbols, num_symbols, intervals, year, month, startDate, endDate, folder, checksum)
