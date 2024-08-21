from .instruction_converter import InstructionConverter, ParseState


class VMConverter:
    instructions: list[InstructionConverter]
    parse_state: ParseState

    def __init__(self, lines: list[str]):
        self.instructions = []
        self.parse_state = ParseState()
        for line in lines:
            normalized_line = self._normalize_line(line)
            if not normalized_line:
                continue
            self.instructions.append(InstructionConverter(normalized_line, self.parse_state))

    @staticmethod
    def _normalize_line(line: str) -> str:
        """
        Delete comments and strip whitespace
        """
        comment_index = line.find('//')
        if comment_index != -1:
            line = line[:comment_index]
        return line.strip()

    def convert_all(self) -> list[str]:
        result = []
        for inst in self.instructions:
            result.extend(inst.convert())
        return result
