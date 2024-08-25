import sys
import hackvm

if __name__ == '__main__':
    vm_code = []
    for vm_filename in sys.argv[1:]:
        vm_file = open(vm_filename, 'r')
        vm_code.extend(vm_file.readlines())

    converter = hackvm.VMConverter(vm_code)
    export_filename = 'out.asm'
    export_file = open(export_filename, 'w')
    export_data = '\n'.join(converter.convert_all())
    export_file.write(export_data)
