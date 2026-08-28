"""初始化 Public Sandbox 所需的全部匿名化样例数据。"""

from __future__ import annotations

from src.demo.generator import seed_all


def main() -> None:
    outputs = seed_all()
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()

