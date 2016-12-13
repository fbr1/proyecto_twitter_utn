import json

with open('results/cosine-minhash-eac/N6300_100_eac_kmeans.json', 'r') as infile:
    confusion_matrix_s = json.load(infile)

confusion_matrix_s = confusion_matrix_s[0:50]

average_confusion_matrix = [[0,0],[0,0]]

for conf_mat in confusion_matrix_s:
    for i in range(2):
        for j in range(2):
            average_confusion_matrix[i][j] += conf_mat[i][j]

for k in range(2):
    for l in range(2):
        average_confusion_matrix[k][l] /= 50

for m in range(2):
    for n in range(2):
        print(average_confusion_matrix[m][n], end='  ')
    print('\n')

print((average_confusion_matrix[0][0]*2409 + average_confusion_matrix[1][1]*3901)/6300)


