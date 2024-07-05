class InstructionParser:
    sp_inst: list[str]

    def __init__(self, instruction: str):
        self.sp_inst = instruction.split()

    def convert(self) -> list[str]:
        opcode = self.sp_inst[0]
        if opcode == 'push':
            num = self.sp_inst[2]
            return [
                f'@{num}',
                'D=A',
                '@SP',
                'A=M',
                'M=D',
                'D=A+1',
                '@SP',
                'M=D'
            ]
        elif opcode == 'add':
            return [
                '@SP',
                'A=M',
                'A=A-1',
                'D=M',
                'A=A-1',
                'M=D+M',
                'D=A+1',
                '@SP',
                'M=D'
            ]
        else:
            raise SyntaxError(f'unknown instruction: {opcode}')
