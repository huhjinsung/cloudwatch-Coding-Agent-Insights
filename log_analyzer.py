import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional
from logger import get_logger

logger = get_logger(__name__)


class LogAnalyzer:
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.logs = []
        self.stats = defaultdict(int)

    def load_logs(self, log_file: Optional[str] = None) -> bool:
        """로그 파일을 로드합니다."""
        file_path = log_file or self.log_file
        if not file_path:
            logger.error("로그 파일 경로가 지정되지 않았습니다.")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        self.logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
            logger.info(f"{len(self.logs)}개의 로그 항목을 로드했습니다.")
            return True
        except Exception as e:
            logger.error(f"로그 파일 로드 실패: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """로그의 기본 통계를 계산합니다."""
        if not self.logs:
            return {}

        stats = {
            "total_logs": len(self.logs),
            "level_distribution": defaultdict(int),
            "agent_distribution": defaultdict(int),
            "error_count": 0,
            "warning_count": 0,
            "info_count": 0,
        }

        for log in self.logs:
            level = log.get("level", "UNKNOWN")
            stats["level_distribution"][level] += 1

            agent = log.get("agent", "unknown")
            stats["agent_distribution"][agent] += 1

            if level == "ERROR":
                stats["error_count"] += 1
            elif level == "WARNING":
                stats["warning_count"] += 1
            elif level == "INFO":
                stats["info_count"] += 1

        stats["level_distribution"] = dict(stats["level_distribution"])
        stats["agent_distribution"] = dict(stats["agent_distribution"])

        return stats

    def filter_by_level(self, level: str) -> List[Dict[str, Any]]:
        """특정 로그 레벨로 필터링합니다."""
        return [log for log in self.logs if log.get("level") == level.upper()]

    def filter_by_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """특정 에이전트의 로그를 필터링합니다."""
        return [log for log in self.logs if log.get("agent") == agent_name]

    def filter_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """시간 범위로 필터링합니다."""
        filtered = []
        for log in self.logs:
            try:
                log_time = datetime.fromisoformat(log.get("timestamp", ""))
                if start_time <= log_time <= end_time:
                    filtered.append(log)
            except ValueError:
                continue
        return filtered

    def get_errors(self) -> List[Dict[str, Any]]:
        """모든 에러 로그를 반환합니다."""
        return self.filter_by_level("ERROR")

    def get_recent_logs(self, count: int = 10) -> List[Dict[str, Any]]:
        """최근 로그를 반환합니다."""
        return self.logs[-count:] if self.logs else []

    def print_summary(self) -> None:
        """로그 요약을 출력합니다."""
        stats = self.get_statistics()
        if not stats:
            print("분석할 로그가 없습니다.")
            return

        print("\n" + "="*50)
        print("로그 분석 결과")
        print("="*50)
        print(f"총 로그 수: {stats['total_logs']}")
        print(f"에러: {stats['error_count']} | 경고: {stats['warning_count']} | 정보: {stats['info_count']}")
        print("\n로그 레벨 분포:")
        for level, count in stats["level_distribution"].items():
            print(f"  {level}: {count}")
        print("\n에이전트 분포:")
        for agent, count in stats["agent_distribution"].items():
            print(f"  {agent}: {count}")
        print("="*50 + "\n")


if __name__ == "__main__":
    analyzer = LogAnalyzer()
    print("LogAnalyzer가 준비되었습니다.")
