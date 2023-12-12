"""
📌 Напишите код, который запускается из командной строки и получает на вход путь до директории на ПК.
📌 Соберите информацию о содержимом в виде объектов namedtuple.
📌 Каждый объект хранит:
○ имя файла без расширения или название каталога,
○ расширение, если это файл,
○ флаг каталога,
○ название родительского каталога.
📌 В процессе сбора сохраните данные в текстовый файл используя логирование."""

import argparse
import csv
import json
import logging
import pickle
import os
from collections import namedtuple
from pathlib import Path


WorkStatus = namedtuple("WorkStatus", ["obj_name", "extension", "is_catalog", "parent_catalog"])


def mk_space(work_dir, work_name="new_file", work_size=220):
    """Ф-ция создаёт файл и записывает размер в байтах и путь к нему если он не существует"""
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    file_path = os.path.join(work_dir, work_name)

    with open(file_path, 'wb') as file:
        file.write(b'\0' * work_size)


def get_work_size(work_path):
    """Ф-ция определяет размер директории по указаному пути"""
    total_size = 0
    for work_dirpath, work_dirnames, work_files in os.walk(work_path):
        for file in work_files:
            file_path = os.path.join(work_dirpath, file)
            total_size += os.path.getsize(file_path)
    return total_size


def save_directory_info(work_path):
    """Ф-ция рекурсивного обхода директории, включая вложенные все вложенные каталоги и файлы.
    Добавляет заданную информацию в файлы JSON, CSV и pickle"""
    res_lst = []
    for work_dirpath, work_dirnames, work_files in os.walk(work_path, topdown=True, onerror=None, followlinks=False):
        work_dirinfo = {'path': work_dirpath, 'type': 'directory', 'size': get_work_size(work_dirpath)}
        res_lst.append(work_dirinfo)
        for file in work_files:
            file_path = os.path.join(work_dirpath, file)
            file_info = {'path': file_path, 'type': 'file', 'size': os.path.getsize(file_path)}
            res_lst.append(file_info)
    save_path = os.path.join(os.path.dirname(work_path), os.path.basename(work_path))

    with open(f'{save_path}.json', 'w') as json_file:
        json.dump(res_lst, json_file, indent=4)

    with open(f'{save_path}.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['path', 'type', 'size'])
        for result in res_lst:
            writer.writerow([result['path'], result['type'], result['size']])

    with open(f'{save_path}.pickle', 'wb') as pickle_file:
        pickle.dump(res_lst, pickle_file)


def read_results_to_json(fl_name: str):
    with open(fl_name, 'r', newline='', encoding='UTF-8') as fl:
        data_jsn = json.load(fl)
        data_jsn_out = [row_pcl for row_pcl in data_jsn]
    return data_jsn_out


def read_results_to_pickle(fl_name: str):
    with open(fl_name, 'rb') as f:
        data_pcl = pickle.load(f)
        data_pcl_out = [row_pcl for row_pcl in data_pcl]
    return data_pcl_out


def read_results_to_csv(fl_name: str):
    with open(fl_name, 'r', newline='') as f:
        data_csv = csv.reader(f)
        data_csv_out = [row for row in data_csv]
    return data_csv_out


def reserching(work_path):
    """Ф-ция рекурсивного обхода директории, включая вложенные все вложенные. Добавляет в список значения аргумнтов"""
    res_lst_r = []
    for work_dirpath, work_dirnames, work_files in os.walk(work_path, topdown=True, onerror=None, followlinks=False):
        obj_name = os.path.basename(work_dirpath)

        parent_catalog = os.path.dirname(work_dirpath)
        res_lst_r.append(WorkStatus(obj_name, None, True, parent_catalog))
        for file in work_files:
            file_path = os.path.join(work_dirpath, file)
            parent_catalog = os.path.dirname(file_path)
            if "." in file:
                file_extension, *file_name = file.split(".")
                file_name = ".".join(file_name)
            else:
                file_name = file
                file_extension = None
            res_lst_r.append(WorkStatus(file_name, file_extension, False, parent_catalog))

    return res_lst_r


def create_log(work_path):
    """ Ф-ция создает файл лога в той же директории"""
    log_file_name = str(os.path.basename(work_path) + ".log")
    work_log_name = os.path.join(os.path.dirname(work_path), log_file_name)

    logging.basicConfig(
        filename=work_log_name, filemode='w', encoding='utf-8', level=logging.INFO, format='{levelname:<8} - {asctime}, {msg}', style='{')
    my_logger = logging.getLogger(__name__)
    res = reserching(work_path)
    for r in res:
        my_logger.info(r.__str__())


def create_drct():
    """ Ф-ция создает тестовые файл и директории"""
    my_path = Path().cwd() / "my_dz_15" / "file_catalog"
    mk_space(my_path, "file_1")
    my_path = Path().cwd() / "my_dz_15" / "file_catalog" / "file_2"
    mk_space(my_path, "file_2", 1400)
    my_path = Path().cwd() / "my_dz_15" / "file_catalog" / "file_3"
    mk_space(my_path, "file_3", 520)
    mk_space(my_path, "file_4", 440)
    my_path = Path().cwd() / "my_dz_15" / "file_catalog"

    save_directory_info(my_path)
    print(*read_results_to_json('./my_dz_15/file_catalog.json'))


def main():
    parser = argparse.ArgumentParser(description="Собирать информацию о содержимом в виде объектов namedtuple.")
    parser.add_argument("folder", nargs="?", type=str, help="Указать путь к папке")
    args = parser.parse_args()
    print(f'В скрипт передано: {args}')
    if os.path.exists(args.folder):
        create_log(args.folder)
    else:
        print("Указанный путь к файлу или директории не существует!")


if __name__ == "__main__":
    # create_drct()
    main()
