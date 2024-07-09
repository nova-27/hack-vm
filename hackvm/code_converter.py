from .instruction_parser import InstructionParser


class CodeConverter:
    instructions: list[InstructionParser]

    def __init__(self, lines: list[str]):
        self.instructions = []
        for line in lines:
            normalized_line = self._normalize_line(line)
            if not normalized_line:
                continue
            self.instructions.append(InstructionParser(normalized_line))

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
        result: list[str] = []
        label_id: int = 0
        for inst in self.instructions:
            converted = inst.convert(label_id)
            result.extend(converted[0])
            label_id = converted[1]
        return result
