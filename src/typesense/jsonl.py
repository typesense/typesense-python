"""
Line splitting for JSONL document exports.

Lines are split on the ``\\n`` byte before anything is decoded. ``str.splitlines``,
and httpx's ``iter_lines`` with it, also split on U+2028, U+2029 and U+0085, which
JSON allows unescaped inside strings, so they would break valid documents apart.
Lines are otherwise left as they arrived: ``\\r`` and blank lines are kept.
"""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class JSONLSplitter:
    """Incremental splitter that turns response bytes into lines."""

    def __init__(self) -> None:
        """Initialize an empty splitter."""
        # Kept as pieces and joined once per line. Appending to a bytes buffer
        # copies it every time, which is quadratic for a large document.
        self._pending: typing.List[bytes] = []

    def feed(self, chunk: bytes) -> typing.List[bytes]:
        """
        Split a chunk of the response body.

        Args:
            chunk (bytes): The next bytes read from the response.

        Returns:
            List[bytes]: The lines completed by this chunk, without their ``\\n``.
        """
        lines: typing.List[bytes] = []
        start = 0
        while (end := chunk.find(b"\n", start)) != -1:
            if self._pending:
                self._pending.append(chunk[start:end])
                lines.append(b"".join(self._pending))
                self._pending.clear()
            else:
                lines.append(chunk[start:end])
            start = end + 1
        if start < len(chunk):
            self._pending.append(chunk[start:])
        return lines

    def flush(self) -> typing.List[bytes]:
        """
        Return the unterminated last line. Call this only after a complete body.

        Typesense does not end an export with ``\\n``, so the last document is
        always returned here.

        Returns:
            List[bytes]: The last line, or nothing if the body ended with ``\\n``.
        """
        if not self._pending:
            return []
        line = b"".join(self._pending)
        self._pending.clear()
        return [line]
