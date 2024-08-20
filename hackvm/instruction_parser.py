SYMBOLS = {'argument': 'ARG', 'local': 'LCL', 'this': 'THIS', 'that': 'THAT'}


class InstructionParser:
    sp_inst: list[str]

    def __init__(self, instruction: str):
        self.sp_inst = instruction.split()

    def convert(self, label_id: int) -> (list[str], int):
        opcode = self.sp_inst[0]
        if opcode == 'push':
            seg = self.sp_inst[1]
            num = int(self.sp_inst[2])

            asm: list[str]
            if seg == 'constant':
                asm = [
                    f'@{num}',
                    'D=A'
                ]
            elif seg in SYMBOLS:
                asm = [
                    f'@{num}',
                    'D=A',
                    f'@{SYMBOLS[seg]}',
                    'A=D+M',
                    'D=M'
                ]
            elif seg == 'pointer':
                asm = [
                    f'@{3 + num}',
                    'D=M'
                ]
            elif seg == 'temp':
                asm = [
                    f'@{5 + num}',
                    'D=M'
                ]
            elif seg == 'static':
                # TODO: VMファイル名を含める
                asm = [
                    f'@Test.{num}',
                    'D=M'
                ]
            else:
                raise SyntaxError(f'unknown segment: {seg}')

            asm.extend([
                '@SP',
                'A=M',
                'M=D',
                'D=A+1',
                '@SP',
                'M=D'
            ])

            return asm, label_id
        elif opcode == 'pop':
            seg = self.sp_inst[1]
            num = int(self.sp_inst[2])

            asm: list[str]
            if seg in SYMBOLS:
                asm = [
                    f'@{num}',
                    'D=A',
                    f'@{SYMBOLS[seg]}',
                    'D=D+M'
                ]
            elif seg == 'pointer':
                asm = [
                    f'@{3 + num}',
                    'D=A'
                ]
            elif seg == 'temp':
                asm = [
                    f'@{5 + num}',
                    'D=A'
                ]
            elif seg == 'static':
                # TODO: VMファイル名を含める
                asm = [
                    f'@Test.{num}',
                    'D=A'
                ]
            else:
                raise SyntaxError(f'unknown segment: {seg}')

            asm.extend([
                '@R13',
                'M=D',
                '@SP',
                'AM=M-1',
                'D=M',
                '@R13',
                'A=M',
                'M=D'
            ])

            return asm, label_id
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
