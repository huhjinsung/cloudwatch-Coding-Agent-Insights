import time
import statistics
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from logger import get_logger

logger = get_logger(__name__)


class PerformanceTracker:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_times = {}
        self.counters = defaultdict(int)

    def record_metric(self, name: str, value: float, agent: Optional[str] = None) -> None:
        """메트릭을 기록합니다."""
        key = f"{agent}:{name}" if agent else name
        self.metrics[key].append({
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        logger.debug(f"메트릭 기록: {key} = {value}")

    def start_timer(self, name: str) -> None:
        """타이머를 시작합니다."""
        self.start_times[name] = time.time()

    def stop_timer(self, name: str, agent: Optional[str] = None) -> float:
        """타이머를 종료하고 소요 시간을 기록합니다."""
        if name not in self.start_times:
            logger.warning(f"시작되지 않은 타이머: {name}")
            return 0.0

        elapsed = time.time() - self.start_times[name]
        self.record_metric(f"{name}_duration", elapsed, agent)
        del self.start_times[name]
        return elapsed

    def increment_counter(self, name: str, agent: Optional[str] = None) -> None:
        """카운터를 증가시킵니다."""
        key = f"{agent}:{name}" if agent else name
        self.counters[key] += 1

    def get_counter(self, name: str, agent: Optional[str] = None) -> int:
        """카운터 값을 조회합니다."""
        key = f"{agent}:{name}" if agent else name
        return self.counters[key]

    def get_metric_stats(self, name: str, agent: Optional[str] = None) -> Dict[str, Any]:
        """메트릭의 통계를 계산합니다."""
        key = f"{agent}:{name}" if agent else name

        if key not in self.metrics or not self.metrics[key]:
            return {}

        values = [m["value"] for m in self.metrics[key]]

        return {
            "name": name,
            "agent": agent,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "sum": sum(values)
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        """모든 메트릭을 반환합니다."""
        result = {}
        for key in self.metrics:
            agent = None
            metric_name = key
            if ":" in key:
                agent, metric_name = key.split(":", 1)
            result[key] = self.get_metric_stats(metric_name, agent)
        return result

    def get_all_counters(self) -> Dict[str, int]:
        """모든 카운터를 반환합니다."""
        return dict(self.counters)

    def track_execution(self, func: Callable) -> Callable:
        """함수 실행을 추적하는 데코레이터입니다."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            self.start_timer(func_name)
            self.increment_counter(f"{func_name}_calls")

            try:
                result = func(*args, **kwargs)
                self.increment_counter(f"{func_name}_success")
                return result
            except Exception as e:
                self.increment_counter(f"{func_name}_error")
                logger.error(f"{func_name} 실행 중 오류: {e}")
                raise
            finally:
                self.stop_timer(func_name)

        return wrapper

    def print_summary(self) -> None:
        """성능 요약을 출력합니다."""
        print("\n" + "="*60)
        print("성능 추적 요약")
        print("="*60)

        if self.metrics:
            print("\n메트릭 통계:")
            for key, stats in self.get_all_metrics().items():
                if stats:
                    print(f"\n  {key}:")
                    print(f"    개수: {stats['count']}")
                    print(f"    평균: {stats['mean']:.4f}")
                    print(f"    최소: {stats['min']:.4f}")
                    print(f"    최대: {stats['max']:.4f}")
                    print(f"    표준편차: {stats['stdev']:.4f}")

        if self.counters:
            print("\n카운터:")
            for key, value in self.get_all_counters().items():
                print(f"  {key}: {value}")

        print("="*60 + "\n")

    def reset(self) -> None:
        """모든 메트릭과 카운터를 초기화합니다."""
        self.metrics.clear()
        self.counters.clear()
        self.start_times.clear()
        logger.info("성능 추적이 초기화되었습니다.")


# 전역 인스턴스
_tracker = PerformanceTracker()


def get_tracker() -> PerformanceTracker:
    """전역 성능 추적기를 반환합니다."""
    return _tracker


if __name__ == "__main__":
    tracker = get_tracker()

    # 테스트
    @tracker.track_execution
    def sample_function():
        time.sleep(0.1)
        return "완료"

    sample_function()
    tracker.print_summary()
