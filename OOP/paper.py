from abc import ABC, abstractmethod
from dataclasses import dataclass
import math
from typing import Any
from pydantic import BaseModel, Field, ValidationError, field_validator


# ==========================================
# 1. CẤU HÌNH PYDANTIC & DATACLASS BÁO CÁO
# ==========================================

class SoftmaxConfig(BaseModel):
    temperature: float = Field(gt=0, allow_inf_nan=False)

    @field_validator("temperature", mode="before")
    @classmethod
    def reject_non_numeric(cls, v: Any) -> float:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError("temperature phải là số thực (int hoặc float).")
        return float(v)


class ScoresInput(BaseModel):
    scores: list[float] = Field(min_length=1)

    @field_validator("scores", mode="before")
    @classmethod
    def check_container_and_elements(cls, v: Any) -> list[float]:
        if not isinstance(v, (list, tuple)):
            raise ValueError("Đầu vào scores phải là list hoặc tuple.")
        cleaned: list[float] = []
        for item in v:
            if isinstance(item, bool) or not isinstance(item, (int, float)):
                raise ValueError(f"Phần tử không hợp lệ: {item!r}. Chỉ chấp nhận số thực.")
            cleaned.append(float(item))
        return cleaned

    @field_validator("scores", mode="after")
    @classmethod
    def check_finite_values(cls, v: list[float]) -> list[float]:
        for item in v:
            if not math.isfinite(item):
                raise ValueError("scores không được chứa NaN, +inf hoặc -inf.")
        return v


@dataclass(frozen=True)
class InferenceReport:
    layer_name: str
    temperature: float
    probabilities: list[float]


# ==========================================
# 2. THIẾT KẾ LỚP TRỪU TƯỢNG & LỚP KẾ THỪA
# ==========================================

class BaseNormalizer(ABC):
    def __init__(self, temperature: float = 1.0) -> None:
        self.temperature = temperature

    @property
    def temperature(self) -> float:
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("temperature phải là một số thực.")
        if not math.isfinite(value) or value <= 0:
            raise ValueError("temperature phải lớn hơn 0 và hữu hạn.")
        self._temperature = float(value)

    @staticmethod
    def validate_scores(scores: list[float] | tuple[float, ...]) -> list[float]:
        if not isinstance(scores, (list, tuple)):
            raise ValueError("scores phải là list hoặc tuple, không chấp nhận chuỗi.")
        if len(scores) == 0:
            raise ValueError("scores không được rỗng.")

        validated: list[float] = []
        for x in scores:
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise ValueError(f"Từ chối phần tử không phải số thực: {x!r}")
            if not math.isfinite(x):
                raise ValueError(f"Từ chối giá trị không hữu hạn (NaN/Inf): {x!r}")
            validated.append(float(x))

        ScoresInput(scores=validated)
        return validated

    @classmethod
    def from_config(cls, data: dict) -> "BaseNormalizer":
        config = SoftmaxConfig(**data)
        return cls(temperature=config.temperature)

    @abstractmethod
    def forward(self, scores: list[float] | tuple[float, ...]) -> list[float]:
        pass

    def __call__(self, scores: list[float] | tuple[float, ...]) -> list[float]:
        return self.forward(scores)

    def report(self, scores: list[float] | tuple[float, ...]) -> InferenceReport:
        probs = self.forward(scores)
        return InferenceReport(
            layer_name=self.__class__.__name__,
            temperature=self.temperature,
            probabilities=probs,
        )


class Softmax(BaseNormalizer):
    def forward(self, scores: list[float] | tuple[float, ...]) -> list[float]:
        clean_scores = self.validate_scores(scores)
        exps = [math.exp(x / self.temperature) for x in clean_scores]
        total = sum(exps)
        return [val / total for val in exps]


class StableSoftmax(BaseNormalizer):
    def forward(self, scores: list[float] | tuple[float, ...]) -> list[float]:
        clean_scores = self.validate_scores(scores)
        m = max(clean_scores)
        exps = [math.exp((x - m) / self.temperature) for x in clean_scores]
        total = sum(exps)
        return [val / total for val in exps]


def evaluate_all(layers: list[BaseNormalizer], scores: list[float] | tuple[float, ...]) -> None:
    for layer in layers:
        print([round(v, 4) for v in layer(scores)])


# ==========================================
# 3. BỘ KIỂM THỬ BẮT BUỘC (TEST SUITE)
# ==========================================

if __name__ == "__main__":
    print("=== 1. Kiểm thử chuẩn đề bài ===")
    x = [1.0, 2.0, 3.0]
    normal = Softmax(temperature=1.0)
    stable = StableSoftmax(temperature=1.0)

    print([round(v, 4) for v in normal(x)])  # [0.09, 0.2447, 0.6652]
    print([round(v, 4) for v in stable(x)])  # [0.09, 0.2447, 0.6652]

    large = [1000.0, 1001.0, 1002.0]
    print([round(v, 4) for v in stable(large)])  # [0.09, 0.2447, 0.6652]
    print(round(sum(stable(x)), 8))              # 1.0

    print("\n=== 2. Kiểm thử đa hình với evaluate_all và InferenceReport ===")
    evaluate_all([normal, stable], x)
    rep = stable.report(x)
    print("Report:", rep)

    print("\n=== 3. Kiểm thử temperature = 0 hoặc -1 ===")
    for bad_t in (0, -1):
        try:
            Softmax(temperature=bad_t)
        except ValueError as e:
            print(f"[OK - ValueError trực tiếp với T={bad_t}]: {e}")

        try:
            StableSoftmax.from_config({"temperature": bad_t})
        except ValidationError as e:
            print(f"[OK - ValidationError qua SoftmaxConfig với T={bad_t}]: Bắt lỗi thành công.")

    print("\n=== 4. Kiểm thử dữ liệu rỗng, NaN, Inf và chuỗi ===")
    invalid_inputs: list[Any] = [
        [],
        [1.0, float("nan")],
        [1.0, float("inf")],
        [1.0, float("-inf")],
        "123",
        [1.0, "2.0"],
    ]
    for bad_scores in invalid_inputs:
        try:
            stable(bad_scores)
        except (ValueError, ValidationError) as e:
            print(f"[OK - Từ chối {bad_scores!r}]: {e}")

    print("\n=== 5. Chứng minh trạng thái độc lập giữa hai đối tượng có temperature khác nhau ===")
    low_temp = StableSoftmax.from_config({"temperature": 0.5})
    high_temp = StableSoftmax.from_config({"temperature": 2.0})
    print(f"low_temp (T={low_temp.temperature}):  {[round(v, 4) for v in low_temp(x)]}")
    print(f"high_temp (T={high_temp.temperature}): {[round(v, 4) for v in high_temp(x)]}")
    assert low_temp.temperature != high_temp.temperature
    assert low_temp(x) != high_temp(x)

    print("\n=== 6. Phân biệt OverflowError ở Softmax thường và StableSoftmax với đầu vào lớn ===")
    try:
        normal(large)
    except OverflowError as e:
        print(f"[OK - Softmax thường phát sinh OverflowError với {large}]: {e}")

    stable_large_result = [round(v, 4) for v in stable(large)]
    print(f"[OK - StableSoftmax tính thành công với {large}]: {stable_large_result}")