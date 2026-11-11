# AI 사용 범위: 이 파일 전체
# AI 종류: OpenAI Codex
# AI 사용 목적: 11주차 모듈 1의 건강정보 구조 및 네 가지 파일 입출력 구현
# 사용한 AI 프롬프트:
# "해당 폴더안에 있는 자료를 바탕으로 일단 11주차의 모듈1에대한 파일을 만들껀데
# 참고.txt 파일을 바탕으로 코딩을 하면 되는데 딱 하라는 부분까지만하고
# 나머지는 그 다음 지침이 떨어지지 않는한 하지 말것"
# 사용한 사람: 성명 미제공 (제출 전 본인 이름 기입)
# 사용 날짜: 2026-11-11

"""11주차 모듈 1: 건강정보 저장, 읽기 및 원본 일치 검증."""

import csv
import json
import pickle
from dataclasses import dataclass
from datetime import date
from pathlib import Path


FIELDS = ("id", "name", "birth_year", "gender", "height", "weight", "bmi", "status")


@dataclass
class HealthRecord:
    """한 사람의 건강정보. 키는 cm, 몸무게는 kg이며 BMI와 상태는 임의 입력한다."""

    name: str
    birth_year: int
    gender: str
    height: float
    weight: float
    bmi: float
    status: str
    id: str = ""

    def to_dict(self):
        """건강정보를 파일에 저장할 딕셔너리로 변환한다."""
        return {field: getattr(self, field) for field in FIELDS}

    @classmethod
    def from_dict(cls, data):
        """파일에서 읽은 딕셔너리의 숫자 자료형을 복원하여 객체를 만든다."""
        if not isinstance(data, dict) or set(data) != set(FIELDS):
            raise ValueError("건강정보의 필드가 올바르지 않습니다.")
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            birth_year=int(data["birth_year"]),
            gender=str(data["gender"]),
            height=float(data["height"]),
            weight=float(data["weight"]),
            bmi=float(data["bmi"]),
            status=str(data["status"]),
        )


class HealthRecordManager:
    """건강정보 객체 목록과 JSON, CSV, TXT, PICKLE 입출력을 관리한다."""

    def __init__(self):
        self.records = []

    def add_record(self, record):
        """record에 고유 식별번호를 발급한 뒤 목록에 추가한다."""
        prefix = f"P{date.today().year}-"
        used_ids = {item.id for item in self.records}
        number = 1
        while f"{prefix}{number:04d}" in used_ids:
            number += 1
        record.id = f"{prefix}{number:04d}"
        self.records.append(record)

    def to_dict_list(self):
        """전체 목록을 비교 및 출력에 사용할 딕셔너리 리스트로 반환한다."""
        return [record.to_dict() for record in self.records]

    def display_records(self):
        """현재 목록을 한 사람당 하나의 딕셔너리로 출력한다."""
        for data in self.to_dict_list():
            print(data)

    def _restore_records(self, data):
        """읽어 온 딕셔너리 리스트 전체를 변환한 뒤 현재 목록에 반영한다."""
        if not isinstance(data, list):
            raise ValueError("건강정보 목록은 리스트여야 합니다.")
        self.records = [HealthRecord.from_dict(item) for item in data]
        return self.records

    def _load_failed(self, file_path, error):
        """읽기에 실패하면 오류를 알리고 빈 목록을 반환한다."""
        print(f"읽기 실패 ({file_path}): {error}")
        self.records = []
        return self.records

    def save_json(self, file_path):
        """file_path에 딕셔너리 리스트를 UTF-8 JSON으로 저장한다."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(self.to_dict_list(), file, ensure_ascii=False, indent=4)
            return True
        except (OSError, TypeError, ValueError) as error:
            print(f"저장 실패 ({file_path}): {error}")
            return False

    def load_json(self, file_path):
        """file_path의 JSON을 객체 목록으로 읽고 실패하면 빈 목록을 반환한다."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return self._restore_records(json.load(file))
        except (OSError, ValueError, TypeError) as error:
            return self._load_failed(file_path, error)

    def save_csv(self, file_path):
        """file_path에 헤더가 있는 UTF-8 CSV를 저장한다."""
        try:
            with open(file_path, "w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(self.to_dict_list())
            return True
        except (OSError, ValueError, TypeError, csv.Error) as error:
            print(f"저장 실패 ({file_path}): {error}")
            return False

    def load_csv(self, file_path):
        """file_path의 CSV 헤더와 행을 읽어 건강정보 목록을 복원한다."""
        try:
            with open(file_path, "r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file, strict=True)
                if reader.fieldnames != list(FIELDS):
                    raise ValueError("CSV 헤더가 올바르지 않습니다.")
                return self._restore_records(list(reader))
        except (OSError, ValueError, TypeError, csv.Error) as error:
            return self._load_failed(file_path, error)

    def save_txt(self, file_path):
        """file_path에 헤더 없이 쉼표로 구분한 UTF-8 텍스트를 저장한다."""
        try:
            with open(file_path, "w", encoding="utf-8", newline="") as file:
                # 구분자가 포함된 문자열도 복원되도록 표준 CSV 인용 규칙을 쓴다.
                writer = csv.writer(file)
                for data in self.to_dict_list():
                    writer.writerow([data[field] for field in FIELDS])
            return True
        except (OSError, ValueError, TypeError, csv.Error) as error:
            print(f"저장 실패 ({file_path}): {error}")
            return False

    def load_txt(self, file_path):
        """file_path의 텍스트 행을 필드 순서에 맞춰 건강정보 목록으로 읽는다."""
        try:
            with open(file_path, "r", encoding="utf-8", newline="") as file:
                data = []
                for row in csv.reader(file, strict=True):
                    if len(row) != len(FIELDS):
                        raise ValueError("TXT 행의 필드 수가 올바르지 않습니다.")
                    data.append(dict(zip(FIELDS, row)))
                return self._restore_records(data)
        except (OSError, ValueError, TypeError, csv.Error) as error:
            return self._load_failed(file_path, error)

    def save_pickle(self, file_path):
        """file_path에 딕셔너리 리스트를 PICKLE 이진 형식으로 저장한다."""
        try:
            with open(file_path, "wb") as file:
                pickle.dump(self.to_dict_list(), file)
            return True
        except (OSError, ValueError, TypeError, pickle.PickleError) as error:
            print(f"저장 실패 ({file_path}): {error}")
            return False

    def load_pickle(self, file_path):
        """직접 저장한 PICKLE 파일을 읽어 건강정보 객체 목록으로 복원한다."""
        try:
            # PICKLE은 신뢰할 수 있는 파일만 읽는다.
            with open(file_path, "rb") as file:
                return self._restore_records(pickle.load(file))
        except (
            OSError, ValueError, TypeError, EOFError, pickle.PickleError,
            AttributeError, ImportError, IndexError, OverflowError,
        ) as error:
            return self._load_failed(file_path, error)


def main():
    """임의 건강정보를 네 형식으로 저장하고 다시 읽어 원본과 비교한다."""
    manager = HealthRecordManager()
    # 모듈 1에서는 BMI와 비만도 상태도 임의 데이터로 입력한다.
    manager.add_record(HealthRecord("홍길동", 1995, "남", 175.0, 72.5, 23.67, "과체중"))
    manager.add_record(HealthRecord("김영희", 1998, "여", 162.0, 52.0, 19.81, "정상"))

    print("=== 저장 전 원본 건강정보 ===")
    manager.display_records()
    original = manager.to_dict_list()

    data_dir = Path(__file__).resolve().parent.parent / "data"
    try:
        data_dir.mkdir(exist_ok=True)
    except OSError as error:
        print(f"저장 폴더 생성 실패: {error}")
        return False

    formats = (
        ("JSON", "json", "save_json", "load_json"),
        ("CSV", "csv", "save_csv", "load_csv"),
        ("TXT", "txt", "save_txt", "load_txt"),
        ("PICKLE", "pkl", "save_pickle", "load_pickle"),
    )
    all_matched = True
    for label, extension, save_method, load_method in formats:
        file_path = data_dir / f"health_data.{extension}"
        print(f"\n=== {label} 저장 및 읽기 ===")
        if not getattr(manager, save_method)(file_path):
            all_matched = False
            continue
        print(f"저장 완료: {file_path.name}")

        restored = HealthRecordManager()
        getattr(restored, load_method)(file_path)
        restored.display_records()
        matched = original == restored.to_dict_list()
        print(f"원본과 일치: {matched}")
        all_matched = all_matched and matched

    print("\n검증 결과:", "4가지 파일 모두 원본과 일치" if all_matched else "검증 실패")
    return all_matched


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
