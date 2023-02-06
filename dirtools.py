#ввод пути к файлу
def input_filepath(message):
    f=str(input(f'{message}'))
    f=f.replace('\\', '/') #заменяем все обратные слэши на прямой
    f=f.replace(' ', '') #удаляем пробелы
    return f

#позволяет убрать последнее название заданного файла
#можно добавить в конец либо название нового файла, либо название новой папки
#name_задается строкой
def dir_modify (filename_,name_):
    for i in range(len(filename_)):
        if filename_[i]=='/':
            pp=i
    return filename_[:pp]+'/'+name_