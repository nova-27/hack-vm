SYMBOLS = {'argument': 'ARG', 'local': 'LCL', 'this': 'THIS', 'that': 'THAT'}


class ParseState:
    label_id = 0
    func_name = "global"


class InstructionConverter:
    sp_inst: list[str]

    def __init__(self, instruction: str):
        self.sp_inst = instruction.split()

    def convert(self, state: ParseState) -> list[str]:
        opcode = self.sp_inst[0]
        if opcode == 'function':
            func_name = self.sp_inst[1]
            var_cnt = int(self.sp_inst[2])

            asm = [f'({func_name})']
            state.func_name = func_name

            push0_asm = InstructionConverter('push constant 0').convert(state)
            for i in range(0, var_cnt):
                asm.extend(push0_asm)

            return asm
        elif opcode == 'return':
            asm = []

            asm.extend(InstructionConverter('pop argument 0').convert(state))
            asm.extend([
                '@LCL',
                'D=M',
                '@R13',
                'M=D',
                '@ARG',
                'D=M+1',
                '@SP',
                'M=D',
                '@R13',
                'AM=M-1',
                'D=M',
                '@THAT',
                'M=D',
                '@R13',
                'AM=M-1',
                'D=M',
                '@THIS',
                'M=D',
                '@R13',
                'AM=M-1',
                'D=M',
                '@ARG',
                'M=D',
                '@R13',
                'AM=M-1',
                'D=M',
                '@LCL',
                'M=D',
                '@R13',
                'A=M-1',
                'A=M',
                '0;JMP'
            ])

            return asm
        elif opcode == 'label':
            label = self.sp_inst[1]

            return [
                # TODO: スコープを関数内に限る
                f'(Label.{label})'
            ]
        elif opcode == 'if-goto':
            label = self.sp_inst[1]

            return [
                '@SP',
                'AM=M-1',
                'D=M',
                f'@Label.{label}',
                'D;JNE'
            ]
        elif opcode == 'goto':
            label = self.sp_inst[1]

            return [
                f'@Label.{label}',
                '0;JMP'
            ]
        elif opcode == 'push':
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

            return asm
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

            return asm
        elif opcode in ('add', 'sub', 'and', 'or'):
            exp = {'add': 'D+M', 'sub': 'M-D', 'and': 'D&M', 'or': 'D|M'}
            return [
                '@SP',
                'AM=M-1',
                'D=M',
                'A=A-1',
                f'M={exp[opcode]}',
            ]
        elif opcode in ('eq', 'gt', 'lt'):
            jmp_opcode = f'J{opcode.upper()}'
            state.label_id += 1
            return [
                '@SP',
                'AM=M-1',
                'D=M',
                'A=A-1',
                'D=M-D',
                'M=-1',
                f'@continue{state.label_id - 1}',
                f'D;{jmp_opcode}',
                '@SP',
                'A=M-1',
                'M=0',
                f'(continue{state.label_id - 1})',
            ]
        elif opcode in ('neg', 'not'):
            return [
                '@SP',
                'A=M-1',
                'M=-M' if opcode == 'neg' else 'M=!M',
            ]
        else:
            raise SyntaxError(f'unknown instruction: {opcode}')
