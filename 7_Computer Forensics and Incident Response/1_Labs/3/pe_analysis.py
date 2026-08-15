import pefile, math

pe = pefile.PE('/home/nikita/Downloads/sample2.exe')
print(f'Entrypoint:  0x{pe.OPTIONAL_HEADER.AddressOfEntryPoint:08x}')
print(f'ImageBase:   0x{pe.OPTIONAL_HEADER.ImageBase:08x}')
print(f'Timestamp:   {pe.FILE_HEADER.TimeDateStamp} (0x{pe.FILE_HEADER.TimeDateStamp:08x})')
print(f'Subsystem:   {pe.OPTIONAL_HEADER.Subsystem}')
print(f'Compiled:    {pefile.PE.__module__}')
print()
print(f'{"Section":<12} {"VirtAddr":>12} {"VirtSize":>12} {"RawSize":>10} {"Entropy":>9}')
print('-'*62)
for s in pe.sections:
    data = s.get_data()
    if len(data) > 0:
        freq = [data.count(bytes([i])) for i in range(256)]
        ent = -sum((f/len(data))*math.log2(f/len(data)) for f in freq if f > 0)
    else:
        ent = 0
    name = s.Name.decode(errors='replace').strip('\x00')
    print(f'{name:<12} 0x{s.VirtualAddress:08x}   0x{s.Misc_VirtualSize:08x}   0x{s.SizeOfRawData:08x}   {ent:8.4f}')

print()
print('=== IMPORTS ===')
if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
    for lib in pe.DIRECTORY_ENTRY_IMPORT:
        print(f'\n{lib.dll.decode()}')
        for imp in lib.imports[:15]:
            name = imp.name.decode() if imp.name else f'ord_{imp.ordinal}'
            print(f'  {name}')
else:
    print('No standard imports (packed/protected)')
