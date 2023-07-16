In order to turn your script into an .exe file, follow the steps below. I strongly recommend using PyInstaller for this purpose. You can install it using pip:
pip install pyinstaller

Next, you will need to include the following libraries:

pandas
python_dateutil-2.8.2.dist-info
six-1.16.0.dist-info
pytz
tzdata
numpy
nltk
colorama
regex
tqdm
xlsxwriter
unidecode
requests
certifi
charset_normalizer
idna
urllib3
io


To determine the exact directory where these libraries are located, you can use the following command:

pip show pandas


Finally, navigate to the directory where your .py file is located and run the following command, replacing 'path' with the library path you found:

pyinstaller --onedir --add-data "\path\pandas;pandas" --add-data "\path\python_dateutil-2.8.2.dist-info;python_dateutil-2.8.2.dist-info" --add-data "\path\six-1.16.0.dist-info;six-1.16.0.dist-info" --add-data "\path\pytz;pytz" --add-data "\path\tzdata;tzdata" --add-data "\path\numpy;numpy" --add-data "\path\nltk;nltk" --add-data "\path\colorama;colorama" --add-data "\path\regex;regex" --add-data "\path\tqdm;tqdm" --add-data "\path\xlsxwriter;xlsxwriter" --add-data "\path\unidecode;unidecode" --add-data "\path\requests;requests" --add-data "\path\certifi;certifi" --add-data "\path\charset_normalizer;charset_normalizer" --add-data "\path\idna;idna" --add-data "\path\urllib3;urllib3" --hidden-import=io KPI_automation.py



Note: I used --onedir instead of --onefile because the latter was taking too long to compile. Although it may create a messy output, you can mitigate this by creating shortcuts to the .exe file and the Meta_Engajamento file.
