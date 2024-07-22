# python file to test anything

dict= {
    'target_valueA=' : 10,
    'target_valueB=' : 10,
    'target_valueC=' : 5
}


listofStrings = []

for item in dict:
    dict[item] = dict[item]/10
    listofStrings.append(item+str(dict[item]))
    
print(listofStrings)
string = '&'.join(listofStrings)
print(string)