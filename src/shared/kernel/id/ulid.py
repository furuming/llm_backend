
import ulid


def new_ulid() -> str:
    """新しい ULID 文字列を生成して返す。"""
    return str(ulid.new())