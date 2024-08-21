from collections import OrderedDict
SYMBOLS = OrderedDict((('that', 'THAT'), ('this', 'THIS'), ('argument', 'ARG'), ('local', 'LCL')))


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

            push0_asm = self._push('constant', 0)
            for i in range(0, var_cnt):
                asm.extend(push0_asm)

            return asm
        elif opcode == 'return':
            asm = []

            asm.extend(self._pop('argument', 0))
            asm.extend([
                '@ARG',
                'D=M+1',
                '@R13',
                'M=D',

                '@LCL',
                'D=M',
                '@SP',
                'M=D'
            ])

            for seg in SYMBOLS.values():
                asm.extend(self._pop_d() + [
                    f'@{seg}',
                    'M=D'
                ])

            asm.extend(self._pop_d() + [
                '@R14',
                'M=D',

                '@R13',
                'D=M',
                '@SP',
                'M=D',

                '@R14',
                'A=M',
                '0;JMP'
            ])

            return asm
        elif opcode == 'label':
            label = self.sp_inst[1]
            return [f'({state.func_name}${label})']
        elif opcode == 'if-goto':
            label = self.sp_inst[1]
            return self._pop_d() + [
                f'@{state.func_name}${label}',
                'D;JNE'
            ]
        elif opcode == 'goto':
            label = self.sp_inst[1]
            return [
                f'@{state.func_name}${label}',
                '0;JMP'
            ]
        elif opcode == 'push':
            seg = self.sp_inst[1]
            num = int(self.sp_inst[2])
            return self._push(seg, num)
        elif opcode == 'pop':
            seg = self.sp_inst[1]
            num = int(self.sp_inst[2])
            return self._pop(seg, num)
        elif opcode in ('add', 'sub', 'and', 'or'):
            exp = {'add': 'D+M', 'sub': 'M-D', 'and': 'D&M', 'or': 'D|M'}
            return self._pop_d() + [
                'A=A-1',
                f'M={exp[opcode]}',
            ]
        elif opcode in ('eq', 'gt', 'lt'):
            jmp_opcode = f'J{opcode.upper()}'
            state.label_id += 1
            return self._pop_d() + [
                'A=A-1',
                'D=M-D',
                'M=-1',
                f'@{state.func_name}$COMP{state.label_id - 1}',
                f'D;{jmp_opcode}',
                '@SP',
                'A=M-1',
                'M=0',
                f'({state.func_name}$COMP{state.label_id - 1})',
            ]
        elif opcode in ('neg', 'not'):
            return [
                '@SP',
                'A=M-1',
                'M=-M' if opcode == 'neg' else 'M=!M',
            ]
        else:
            raise SyntaxError(f'unknown instruction: {opcode}')

    def _push(self, segment: str, index: int):
        asm: list[str]

        # copy data to D reg
        if segment == 'constant':
            asm = [
                f'@{index}',
                'D=A'
            ]
        elif segment in SYMBOLS:
            asm = [
                f'@{index}',
                'D=A',
                f'@{SYMBOLS[segment]}',
                'A=D+M',
                'D=M'
            ]
        elif segment == 'pointer':
            asm = [
                f'@{3 + index}',
                'D=M'
            ]
        elif segment == 'temp':
            asm = [
                f'@{5 + index}',
                'D=M'
            ]
        elif segment == 'static':
            # TODO: VMファイル名を含める
            asm = [
                f'@Test.{index}',
                'D=M'
            ]
        else:
            raise SyntaxError(f'unknown segment: {segment}')

        asm.extend([
            '@SP',
            'A=M',
            'M=D',
            '@SP',
            'M=M+1'
        ])

        return asm

    def _pop_d(self):
        return [
            '@SP',
            'AM=M-1',
            'D=M',
        ]

    def _pop(self, segment: str, index: int):
        asm: list[str]

        # store dest addr to D reg
        if segment in SYMBOLS:
            asm = [
                f'@{index}',
                'D=A',
                f'@{SYMBOLS[segment]}',
                'D=D+M'
            ]
        elif segment == 'pointer':
            asm = [
                f'@{3 + index}',
                'D=A'
            ]
        elif segment == 'temp':
            asm = [
                f'@{5 + index}',
                'D=A'
            ]
        elif segment == 'static':
            # TODO: VMファイル名を含める
            asm = [
                f'@Test.{index}',
                'D=A'
            ]
        else:
            raise SyntaxError(f'unknown segment: {segment}')

        asm.extend([
            '@R13',
            'M=D'
        ] + self._pop_d() + [
            '@R13',
            'A=M',
            'M=D'
        ])

        return asm
