### программа раскладывает данные записаные в одну колонку из входной таблицы по столбцам в выходной.


spamtab = []  # temp table for input file
tabdata = []  # tab headers list
fintab = []  # final table


with open('dat2.txt', 'r', encoding='utf-8') as f:
    for line in f:
        words = line.split('\t')
        tablabel = words[0]
        tabtext = words[1][:-1]
        if tablabel != '':                             # - some stroke has more than one cell
            spamtab.append([tablabel, tabtext])
        else:
            spamtab[-1:][0][1] += str(' ' + tabtext)

        if tablabel not in tabdata and tablabel != '':
            tabdata.append(tablabel)


numofcolumns = len(tabdata)

#build final table
for i in range(len(spamtab)//numofcolumns):
    st = []
    for ii in range(numofcolumns):
        z = i*numofcolumns
        st.append(spamtab[z+ii][1])
    print(st)
    fintab.append(st)

#write to file
with open('new_data2.txt', 'w', encoding='utf-8') as f:
    for i in tabdata:
        f.write(f'{i}\t')
    f.write('\n')
    for i in range(len(fintab)):
        for ii in range(len(fintab[i])):
            f.write(f'{fintab[i][ii]}\t')
        f.write('\n')

