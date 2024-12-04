import pyautogui as pa
import pyperclip
from time import sleep

def updateCompatibilityThreshold(newValue):
    '''
    This function updates the compatibility_threshold in the config.txt file.
    '''
    with open('config.txt', 'r') as file:
        lines = file.readlines()

    with open('config.txt', 'w') as file:
        for line in lines:
            if 'compatibility_threshold' in line:
                file.write(f'compatibility_threshold = {newValue}\n')
            else:
                file.write(line)

def updateMaxStagnation(newValue):
    '''
    This function updates the max_stagnation in the config.txt file.
    '''
    with open('config.txt', 'r') as file:
        lines = file.readlines()

    with open('config.txt', 'w') as file:
        for line in lines:
            if 'max_stagnation' in line:
                file.write(f'max_stagnation = {newValue}\n')
            else:
                file.write(line)


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
    
def main():
    sampleAmount = 10

    sleep(2)

    ct = 0.5

    while ct < 10:
        updateCompatibilityThreshold(ct)

        count = 0
        roundData = []
        n = 0
        total = 0
        for _ in range(sampleAmount):
            result = getResult()
            roundData.append(result)
            if result:
                n += 1
                total += result
            else:
                count += 1

        print(f'\nFor CT {ct}:\n{roundData}')
        if count > sampleAmount / 2:
            print('FAILED')
        else:
            print(f'Average of {total/n}')

        ct += 0.2
    

if __name__ == '__main__':
    main()
