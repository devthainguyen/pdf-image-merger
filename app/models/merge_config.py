from dataclasses import dataclass


@dataclass
class MergeConfig:
    input_dir: str
    output_dir: str

    # Khoảng cách giữa 2 scan.
    # 0 = sát nhau.
    separator_width: float = 0.0

    # Màu khoảng cách.
    separator_color: tuple = (255, 255, 255)

    # Nếu True thì yêu cầu PDF chỉ có đúng 1 trang.
    require_single_page: bool = True