import subprocess
import tempfile
from pathlib import Path

from fastapi import HTTPException

from src.modules.rag.services.parser import Parser


class LiteParseParser(Parser):
    """liteparse コマンドを使って各種ファイルからテキストを抽出する。"""

    def parse(self, *, filename: str, content: bytes, content_type: str | None = None) -> str:
        """一時ファイルへ保存した入力を liteparse で解析する。"""
        suffix = Path(filename).suffix or ".bin"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(content)
            input_path = Path(temp_file.name)

        cmd = ["lit", "parse", str(input_path)]

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as e:
            raise HTTPException(status_code=500, detail="lit command not found") from e
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or "").strip()
            raise HTTPException(
                status_code=500,
                detail=f"parse failed: {stderr if stderr else 'unknown error'}",
            ) from e
        finally:
            input_path.unlink(missing_ok=True)

        text = result.stdout.strip()
        if not text:
            raise HTTPException(status_code=500, detail="parse failed: empty output")
        return text
