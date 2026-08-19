import time
import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional
from logger import get_logger

logger = get_logger()


class MetricsCollector:
    """에이전트 호출에 대한 성능 지표를 수집하고 집계합니다."""

    def __init__(self):
        self.records: List[Dict[str, Any]] = []
        self._active: Dict[str, float] = {}

    def start(self, agent_name: str) -> None:
        """에이전트 호출의 시작 시각을 기록합니다."""
        self._active[agent_name] = time.time()

    def stop(self, agent_name: str, success: bool = True, tokens: int = 0) -> Optional[float]:
        """에이전트 호출을 종료하고 소요 시간을 기록합니다."""
        start_time = self._active.pop(agent_name, None)
        if start_time is None:
            logger.warning(f"'{agent_name}'에 대한 시작 기록이 없습니다.")
            return None

        duration = time.time() - start_time
        self.records.append({
            "agent": agent_name,
            "duration": duration,
            "success": success,
            "tokens": tokens,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
        logger.info(f"'{agent_name}' 호출 완료: {duration:.3f}s (성공={success}, 토큰={tokens})")
        return duration

    def record(self, agent_name: str, duration: float, success: bool = True, tokens: int = 0) -> None:
        """이미 측정된 지표를 직접 기록합니다."""
        self.records.append({
            "agent": agent_name,
            "duration": duration,
            "success": success,
            "tokens": tokens,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

    def get_summary(self) -> Dict[str, Any]:
        """수집된 지표의 집계 요약을 반환합니다."""
        if not self.records:
            return {}

        per_agent: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"count": 0, "success": 0, "failure": 0, "total_duration": 0.0, "total_tokens": 0}
        )

        for r in self.records:
            agent = r["agent"]
            per_agent[agent]["count"] += 1
            per_agent[agent]["total_duration"] += r["duration"]
            per_agent[agent]["total_tokens"] += r["tokens"]
            if r["success"]:
                per_agent[agent]["success"] += 1
            else:
                per_agent[agent]["failure"] += 1

        summary = {
            "total_calls": len(self.records),
            "agents": {},
        }

        for agent, data in per_agent.items():
            count = data["count"]
            summary["agents"][agent] = {
                "count": count,
                "success": data["success"],
                "failure": data["failure"],
                "success_rate": round(data["success"] / count, 3) if count else 0.0,
                "avg_duration": round(data["total_duration"] / count, 3) if count else 0.0,
                "total_tokens": data["total_tokens"],
            }

        return summary

    def get_slowest(self, count: int = 5) -> List[Dict[str, Any]]:
        """소요 시간이 가장 긴 호출을 반환합니다."""
        return sorted(self.records, key=lambda r: r["duration"], reverse=True)[:count]

    def export_json(self, file_path: str) -> bool:
        """수집된 지표를 JSON 파일로 저장합니다."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            logger.info(f"{len(self.records)}개의 지표를 '{file_path}'에 저장했습니다.")
            return True
        except Exception as e:
            logger.error(f"지표 저장 실패: {e}")
            return False

    def reset(self) -> None:
        """수집된 지표를 초기화합니다."""
        self.records.clear()
        self._active.clear()

    def print_summary(self) -> None:
        """지표 요약을 출력합니다."""
        summary = self.get_summary()
        if not summary:
            print("수집된 지표가 없습니다.")
            return

        print("\n" + "=" * 50)
        print("에이전트 성능 지표")
        print("=" * 50)
        print(f"총 호출 수: {summary['total_calls']}")
        print("\n에이전트별 지표:")
        for agent, data in summary["agents"].items():
            print(f"  [{agent}]")
            print(f"    호출: {data['count']} | 성공률: {data['success_rate']:.1%}")
            print(f"    평균 소요: {data['avg_duration']:.3f}s | 총 토큰: {data['total_tokens']}")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    collector = MetricsCollector()

    collector.start("DataAnalyzer")
    time.sleep(0.05)
    collector.stop("DataAnalyzer", success=True, tokens=320)

    collector.record("MonitoringAgent", duration=1.42, success=True, tokens=512)
    collector.record("MonitoringAgent", duration=0.88, success=False, tokens=104)

    collector.print_summary()
    print("가장 느린 호출:", collector.get_slowest(2))
