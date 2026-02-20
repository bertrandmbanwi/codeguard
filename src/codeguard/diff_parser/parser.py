import re
from pathlib import Path

from codeguard.diff_parser.models import DiffHunk, FileDiff, ParsedDiff


class UnifiedDiffParser:
    """Parser for unified diff format."""

    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".rb": "ruby",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".tf": "terraform",
        ".json": "json",
        ".xml": "xml",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".sh": "bash",
        ".sql": "sql",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
    }

    @staticmethod
    def detect_language(file_path: str) -> str:
        """Detect programming language from file extension."""
        if file_path.startswith("b/") or file_path.startswith("a/"):
            file_path = file_path[2:]

        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix in UnifiedDiffParser.LANGUAGE_MAP:
            return UnifiedDiffParser.LANGUAGE_MAP[suffix]

        # Check for known binary formats
        if suffix in [".png", ".jpg", ".jpeg", ".gif", ".pdf", ".bin"]:
            return "binary"

        # Default for unknown files
        return "unknown"

    @staticmethod
    def parse(diff_text: str) -> ParsedDiff:
        """Parse unified diff format."""
        files: list[FileDiff] = []
        lines = diff_text.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for file header
            if line.startswith("diff --git"):
                # Parse file paths
                parts = line.split()
                if len(parts) >= 4:
                    old_path = parts[2][2:] if parts[2].startswith("a/") else parts[2]
                    new_path = parts[3][2:] if parts[3].startswith("b/") else parts[3]
                else:
                    i += 1
                    continue

                file_path = new_path if new_path != "/dev/null" else old_path

                # Check for new/deleted files
                is_new = False
                is_deleted = False

                # Scan ahead for index/new file indicators
                j = i + 1
                while j < len(lines) and not lines[j].startswith("diff --git"):
                    if lines[j].startswith("new file"):
                        is_new = True
                    elif lines[j].startswith("deleted file"):
                        is_deleted = True
                    j += 1

                language = UnifiedDiffParser.detect_language(file_path)

                # Skip binary files
                if language == "binary":
                    i = j
                    continue

                file_diff = FileDiff(
                    path=file_path,
                    language=language,
                    is_new=is_new,
                    is_deleted=is_deleted,
                )

                # Parse hunks
                i += 1
                while i < len(lines) and not lines[i].startswith("diff --git"):
                    if lines[i].startswith("@@"):
                        hunk = UnifiedDiffParser._parse_hunk(lines, i)
                        if hunk:
                            file_diff.hunks.append(hunk[0])
                            i = hunk[1]
                        else:
                            i += 1
                    else:
                        i += 1

                files.append(file_diff)
            else:
                i += 1

        return ParsedDiff(files=files)

    @staticmethod
    def _parse_hunk(lines: list[str], start_idx: int) -> tuple[DiffHunk, int] | None:
        """Parse a single hunk starting at @@."""
        hunk_header = lines[start_idx]

        # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
        match = re.search(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", hunk_header)
        if not match:
            return None

        start_line = int(match.group(2))
        end_line = start_line

        hunk_lines: list[str] = []
        added_lines: list[int] = []
        removed_lines: list[int] = []
        context_before: list[str] = []
        context_after: list[str] = []

        i = start_idx + 1
        line_num = start_line
        context_buffer: list[str] = []

        while i < len(lines):
            line = lines[i]

            # Stop at next hunk or file
            if line.startswith("@@") or line.startswith("diff --git"):
                break

            # End of diff
            if line.startswith("---") or line.startswith("+++"):
                break

            # Process diff lines
            if line.startswith("+"):
                if context_buffer:
                    context_before.extend(context_buffer)
                    context_buffer = []
                hunk_lines.append(line[1:])
                added_lines.append(line_num)
                line_num += 1
            elif line.startswith("-"):
                if context_buffer:
                    context_before.extend(context_buffer)
                    context_buffer = []
                hunk_lines.append(line[1:])
                removed_lines.append(line_num)
            elif line.startswith(" "):
                # Context line
                context_buffer.append(line[1:])
                hunk_lines.append(line[1:])
                line_num += 1
            elif line.startswith("\\"):
                # "\ No newline at end of file" marker
                pass
            else:
                # Unexpected format, skip
                pass

            i += 1

        context_after = context_buffer
        end_line = line_num - 1

        hunk = DiffHunk(
            start_line=start_line,
            end_line=end_line,
            added_lines=added_lines,
            removed_lines=removed_lines,
            content="\n".join(hunk_lines),
            context_before="\n".join(context_before),
            context_after="\n".join(context_after),
        )

        return hunk, i
