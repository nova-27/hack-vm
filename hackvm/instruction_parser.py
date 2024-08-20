class InstructionParser:
    sp_inst: list[str]

    def __init__(self, instruction: str):
        self.sp_inst = instruction.split()

    def convert(self, label_id: int) -> (list[str], int):
        opcode = self.sp_inst[0]
        if opcode == 'push':
            num = self.sp_inst[2]
            return ([
                f'@{num}',
                'D=A',
                '@SP',
                'A=M',
                'M=D',
                'D=A+1',
                '@SP',
                'M=D'
            ], label_id)
        elif opcode in ('add', 'sub', 'and', 'or'):
            exp = {'add': 'D+M', 'sub': 'M-D', 'and': 'D&M', 'or': 'D|M'}
            return ([
                '@SP',
                'A=M-1',
                'D=M',
                'A=A-1',
                f'M={exp[opcode]}',
                '@SP',
                'M=M-1'
            ], label_id)
        elif opcode in ('eq', 'gt', 'lt'):
            jmp_opcode = f'J{opcode.upper()}'
            return ([
                '@SP',
                'A=M-1',
                'D=M',
                'A=A-1',
                'D=M-D',
                'M=-1',
                '@SP',
                'M=M-1',
                f'@continue{label_id}',
                f'D;{jmp_opcode}',
                '@SP',
                'A=M-1',
                'M=0',
                f'(continue{label_id})',
            ], label_id + 1)
        elif opcode in ('neg', 'not'):
            return ([
                '@SP',
                'A=M-1',
                'M=-M' if opcode == 'neg' else 'M=!M',
            ], label_id)
        else:
            raise SyntaxError(f'unknown instruction: {opcode}')
