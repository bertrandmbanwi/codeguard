from dataclasses import dataclass, field


@dataclass
class DiffHunk:
    """Represents a hunk in a unified diff."""

    start_line: int
    end_line: int
    added_lines: list[int] = field(default_factory=list)
    removed_lines: list[int] = field(default_factory=list)
    content: str = ""
    context_before: str = ""
    context_after: str = ""


@dataclass
class FileDiff:
    """Represents the diff for a single file."""

    path: str
    language: str
    hunks: list[DiffHunk] = field(default_factory=list)
    is_new: bool = False
    is_deleted: bool = False


@dataclass
class ParsedDiff:
    """Represents a parsed diff containing multiple files."""

    files: list[FileDiff] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        """Total number of files in the diff."""
        return len(self.files)

    @property
    def total_additions(self) -> int:
        """Total number of lines added."""
        count = 0
        for file_diff in self.files:
            for hunk in file_diff.hunks:
                count += len(hunk.added_lines)
        return count

    @property
    def total_deletions(self) -> int:
        """Total number of lines deleted."""
        count = 0
        for file_diff in self.files:
            for hunk in file_diff.hunks:
                count += len(hunk.removed_lines)
        return count
