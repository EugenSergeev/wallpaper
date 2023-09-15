import os
from pathlib import Path
import datetime
import shutil

today = datetime.date.today()
needed_day = today + datetime.timedelta(days=1)
needed_day = needed_day.strftime('%Y%m%d')
packages_to_sort_path = Path(r'd:\NEW_PACKAGES')
copy_path = Path(r'd:\Temp\PMiroshkin\dev\sorted_packages')
list_to_sort = input('Введите список пакетов для отправки\n')
list_to_sort = list_to_sort.split('+')
final_list = []

for files in copy_path.iterdir():
    os.remove(files)

for name in list_to_sort:
    name = '643' + name
    final_list.append(name)


for package in packages_to_sort_path.iterdir():
    if needed_day in package.name:
        shutil.copy2(package, copy_path)

for package in copy_path.iterdir():
    should_keep = False
    for name in final_list:
        if name in package.name:
            should_keep = True
            break

    if should_keep:
        print(f'Оставляем пакет {package.name}')
    else:
        os.remove(package)