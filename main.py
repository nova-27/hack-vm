import sys
import hackvm

if __name__ == '__main__':
    vm_filename = sys.argv[1]
    vm_file = open(vm_filename, 'r')
    converter = hackvm.CodeConverter(vm_file.readlines())

    export_filename = vm_filename[:vm_filename.rfind('.')] + '.asm'
    export_file = open(export_filename, 'w')
    export_data = '\n'.join(converter.convert_all())
    export_file.write(export_data)
