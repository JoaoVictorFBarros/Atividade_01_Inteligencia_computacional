from bs4 import BeautifulSoup
import csv

html_file_path = './page.html'

with open(html_file_path, 'r', encoding='utf-8') as html_file:
    html_content = html_file.read()

soup = BeautifulSoup(html_content, 'html.parser')
class_prefix = 'datatable_cell__LJp3C datatable_cell--align-end__qgxDQ'

soup = BeautifulSoup(html_content, 'html.parser')
elements_with_class = soup.select(f'[class^="{class_prefix}"]')

cont = 1

class Row:
    def __init__(self):
        self.date = 0
        self.last = 0
        self.open = 0
        self.min = 0
        self.max = 0
        self.vol = 0
        self.var = 0
    def printrow(self):
       return("Data: " + str(self.date) + "\nUltimo: " + str(self.last) + "\nAbertura: " + str(self.open) +
      "\nMax: " + str(self.max) + "\nMin: " + str(self.min) +
      "\nVol: " + str(self.vol) + "\nVar: " + str(self.var) + "\n\n")

rows = []
for element in range(0,int(len(elements_with_class)/6)):
    newrow = Row()
    newrow.last = elements_with_class[cont].getText().replace(",",".")
    newrow.open = elements_with_class[cont +1].getText().replace(",",".")
    newrow.max = elements_with_class[cont +2].getText().replace(",",".")
    newrow.min = elements_with_class[cont +3].getText().replace(",",".")
    newrow.vol = elements_with_class[cont +4].getText().replace("K","").replace(",",".")
    newrow.var = elements_with_class[cont +5].getText().replace(",",".").replace("%","")
    
    rows.append(newrow)
    cont+=6

time_tags = soup.find_all('time')

cont=0
for time in time_tags:
    rows[cont].date = time.getText()
    cont+=1
      
rows = [row for row in rows if row.date != 0]

#Missing values
for row in rows:
    if len(row.date) == 0 or len(row.last) == 0 or len(row.open) == 0 or len(row.max) == 0 or len(row.min) == 0 or len(row.vol) == 0 or len(row.var) == 0:
        
        neighbor_vols = []

        for offset in range(-5, 6):
            try:
                neighbor_vols.append(float(rows[cont + offset].vol))
            except (IndexError, ValueError):
                continue

        total_vol = sum(neighbor_vols)
        if len(neighbor_vols) > 0:
            row.vol = total_vol / len(neighbor_vols)
        else:
            row.vol = 0.0
rows = rows[1:]  

#Normalize
def normalize(data):
    min_val = min(data)
    max_val = max(data)
    normalized_data = [(x - min_val) / (max_val - min_val) for x in data]
    return normalized_data

last=[]
opencol=[]
mincol=[]
maxcol=[]
vol=[]
var=[]
for row in rows:
    last.append(float(row.last))
    opencol.append(float(row.open))
    mincol.append(float(row.min))
    maxcol.append(float(row.max))
    vol.append(float(row.vol))
    var.append(float(row.var))

last = normalize(last)
opencol = normalize(opencol)
mincol = normalize(mincol)
maxcol = normalize(maxcol)
vol = normalize(vol)
var = normalize(var)

cont=0
for row in rows:
    row.last = last[cont]
    row.open = opencol[cont]
    row.min = mincol[cont]
    row.max = maxcol[cont]
    row.vol = vol[cont]
    row.var = var[cont]
    cont+=1

f = open("data.txt", "w")

for row in rows:
    f.write(row.printrow())
    
    
fieldnames = ["Data", "Ultimo", "Abertura", "Max", "Min", "Vol", "Var"]

with open("data.csv", mode="w", newline="") as csvfile:
    
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in rows:
        row_dict = {
            "Data": row.date,
            "Ultimo": row.last,
            "Abertura": row.open,
            "Max": row.max,
            "Min": row.min,
            "Vol": row.vol,
            "Var": row.var
        }
        writer.writerow(row_dict)
print("Done.\n\n")
