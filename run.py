import pyautogui as pa
import pyperclip
from time import sleep

def getResult():
    pyperclip.copy('nah')
    pa.write('python main.py')
    pa.press('enter')
    while pyperclip.paste() == 'nah':
        sleep(1)
    
    try:
        r = int(pyperclip.paste())
        pyperclip.copy('nah')
        return r
    except:
        pyperclip.copy('nah')
        return None
    

amount = 10

sleep(2)

count = 0
data = []
n = 0
total = 0
for i in range(amount):
    result = getResult()
    data.append(result)
    if result:
        n += 1
        total += result
    else:
        count += 1

print(f'\n\n{data}\n\n')
if count > amount / 2:
    print('FAILED')
else:
    print(f'Average of {total/n}')

