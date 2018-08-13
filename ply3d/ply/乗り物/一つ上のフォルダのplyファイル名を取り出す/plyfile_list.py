import os
plyfolder_path = '..'
ply_file = []
for file in os.listdir(plyfolder_path):
    str = []
    if file.endswith(".ply"):
        str += os.path.splitext(file)[0]
        ply_file.append(''.join(str))
print(ply_file)
